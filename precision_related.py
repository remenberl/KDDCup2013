#-*- coding: UTF-8 -*-
from sklearn.preprocessing import normalize
from custom_setting import *
from name import *
from difflib import SequenceMatcher


def local_clustering(potential_duplicate_groups, coauthor_matrix, covenue_matrix, author_word_matrix):
    """Detect duplicate groups based on coauthor relationship between authors.

    Parameters:
        potential_duplicate_groups:
            A set containing lots of tuples describing the potential duplicate group.
        coauthor_matrix:
            A sparse matrix with row: author_id and column: author_id.
            It is obtained from author_paper_matrix.

    Returns:
        A set containing lots of tuples describing the real duplicate group.
    """
    real_duplicate_groups = set()
    print "\tIn total " + str(len(potential_duplicate_groups)) + " groups:"
    count = 0

    similarity_dict = dict()
    author_group_feature_dict = dict()
    normalized_author_group_feature_dict = dict()

    statistic = [0] * 5
    for group in potential_duplicate_groups:
        local_author_group_set = set()
        local_similarity_set = set()

        count += 1
        if count % 500 == 0:
            print "\tFinish analysing " \
                + str(float(count)/len(potential_duplicate_groups)*100) \
                + "% (" + str(count) + "/" + str(len(potential_duplicate_groups)) \
                + ") possible duplicate groups."
            print "\tStatistic about merges based on different features: " + str(statistic)
        # If there is only one author_id in the group, pass
        if len(group) == 1:
            real_duplicate_groups.add(group)
            continue

        # Treat coauthors for a particular author as features and normalize it
        for author in group:
            local_author_group_set.add((author,))
            if (author,) not in author_group_feature_dict:
                author_group_feature_dict[(author,)] = (coauthor_matrix.getrow(author), covenue_matrix.getrow(author), author_word_matrix.getrow(author))
                normalized_author_group_feature_dict[(author,)] = (
                    normalize(author_group_feature_dict[(author,)][0], norm='l2', axis=1),
                    normalize(author_group_feature_dict[(author,)][1], norm='l2', axis=1),
                    normalize(author_group_feature_dict[(author,)][2], norm='l2', axis=1))
        # Compute Cosine similarity between every pair of potential duplicate authors in the group
        for author_A in group:
            for author_B in group:
                if author_A < author_B:
                    local_similarity_set.add(((author_A,), (author_B,)))
                    if ((author_A,), (author_B,)) not in similarity_dict:
                        # tmp = normalized_author_group_feature_dict[(author_A,)][0] + normalized_author_group_feature_dict[(author_A,)][1]
                        similarity_dict[((author_A,), (author_B,))] \
                            = ((normalized_author_group_feature_dict[(author_A,)][0]
                               * normalized_author_group_feature_dict[(author_B,)][0].transpose())[0, 0],
                               (normalized_author_group_feature_dict[(author_A,)][1]
                                   * normalized_author_group_feature_dict[(author_B,)][1].transpose())[0, 0],
                               (normalized_author_group_feature_dict[(author_A,)][0]
                                   * normalized_author_group_feature_dict[(author_B,)][1].transpose())[0, 0],
                               (normalized_author_group_feature_dict[(author_A,)][1]
                                   * normalized_author_group_feature_dict[(author_B,)][0].transpose())[0, 0],
                               (normalized_author_group_feature_dict[(author_A,)][2]
                                  * normalized_author_group_feature_dict[(author_B,)][2].transpose())[0, 0])
                        similarity_dict[((author_A,), (author_B,))] = \
                            (coauthor_weight * similarity_dict[((author_A,), (author_B,))][0],
                                covenue_weight * similarity_dict[((author_A,), (author_B,))][1],
                                author_venue_weight * similarity_dict[((author_A,), (author_B,))][2],
                                author_venue_weight * similarity_dict[((author_A,), (author_B,))][3],
                                paper_word_weight * similarity_dict[((author_A,), (author_B,))][4])
                            # = (normalized_author_group_feature_dict[(author_A,)][0]
                            #     + normalized_author_group_feature_dict[(author_A,)][1]
                            #     + normalized_author_group_feature_dict[(author_A,)][2]) \
                            #         * (normalized_author_group_feature_dict[(author_B,)][0]
                            #         + normalized_author_group_feature_dict[(author_B,)][1]
                            #         + normalized_author_group_feature_dict[(author_B,)][2]).transpose()

        while True:
            max_similarity = 0
            max_pair = ()
            # Find the author partition pair with largest similarity
            # and it should be larger than then the threshold
            for author_group_pair in local_similarity_set:
                (max_similarity, max_pair) = (max(similarity_dict[author_group_pair]), author_group_pair) \
                    if max(similarity_dict[author_group_pair]) > merge_threshold else (max_similarity, max_pair)

            # If we cannot find such an author group pair,
            #   output the current duplicate authors in the whole group,
            # else
            #   we merge this pair
            if max_similarity == 0:
                for author_group in local_author_group_set:
                    real_duplicate_groups.add(author_group)
                break
            else:
                statistic[similarity_dict[max_pair].index(max(similarity_dict[max_pair]))] += 1
                # Compute the new feature and normalize it for the merged author group pair
                new_author_group = tuple(sorted(max_pair[0] + max_pair[1]))
                if new_author_group not in author_group_feature_dict:
                    new_feature = tuple([i + j for (i, j) in zip(author_group_feature_dict[max_pair[0]], author_group_feature_dict[max_pair[1]])])
                    author_group_feature_dict[new_author_group] = new_feature
                    normalized_author_group_feature_dict[new_author_group]\
                        = (normalize(author_group_feature_dict[new_author_group][0], norm='l2', axis=1),
                           normalize(author_group_feature_dict[new_author_group][1], norm='l2', axis=1),
                            normalize(author_group_feature_dict[new_author_group][2], norm='l2', axis=1))

                # Remove individual author group in the new merged author group
                local_author_group_set.remove(max_pair[0])
                local_author_group_set.remove(max_pair[1])
                for author_group_pair in set(local_similarity_set):
                    if max_pair[0] in author_group_pair or max_pair[1] in author_group_pair:
                        local_similarity_set.remove(author_group_pair)
                # Compute new similarity between this new group
                # with the rest existing groups
                for author_group in local_author_group_set:
                    new_pair = tuple(sorted((author_group, new_author_group)))
                    local_similarity_set.add(new_pair)
                    if new_pair not in similarity_dict:
                        # tmp = normalized_author_group_feature_dict[author_group][0] + normalized_author_group_feature_dict[new_author_group][1]
                        similarity_dict[new_pair] \
                            = ((normalized_author_group_feature_dict[author_group][0]
                                * normalized_author_group_feature_dict[new_author_group][0].transpose())[0, 0],
                               (normalized_author_group_feature_dict[author_group][1]
                                * normalized_author_group_feature_dict[new_author_group][1].transpose())[0, 0],
                               (normalized_author_group_feature_dict[author_group][0]
                                * normalized_author_group_feature_dict[new_author_group][1].transpose())[0, 0],
                               (normalized_author_group_feature_dict[author_group][1]
                                * normalized_author_group_feature_dict[new_author_group][0].transpose())[0, 0],
                               (normalized_author_group_feature_dict[author_group][2]
                                * normalized_author_group_feature_dict[new_author_group][2].transpose())[0, 0])
                        similarity_dict[new_pair] = \
                            (coauthor_weight * similarity_dict[new_pair][0],
                                covenue_weight * similarity_dict[new_pair][1],
                                author_venue_weight * similarity_dict[new_pair][2],
                                author_venue_weight * similarity_dict[new_pair][3],
                                paper_word_weight * similarity_dict[new_pair][4])
                            # # = (normalized_author_group_feature_dict[author_group][0]
                            #     + normalized_author_group_feature_dict[author_group][1]
                            #     + normalized_author_group_feature_dict[author_group][2]) \
                            #         * (normalized_author_group_feature_dict[new_author_group][0]
                            #         + normalized_author_group_feature_dict[new_author_group][1]
                            #         + normalized_author_group_feature_dict[new_author_group][2]).transpose()
                local_author_group_set.add(new_author_group)
    return real_duplicate_groups


def merge_local_clusters(real_duplicate_groups):
    """Merge local clusters.

    Parameters:
        real_duplicate_groups:
            A set of groups which contain duplicate author_ids separately.

    Returns:
        A dictionary of duplicate authors with key: author id and value:
        a list of duplicate author ids
    """
    id_group_dict = dict()
    print "\tMapping each author to his/her duplicate authors from duplicate groups."
    for group in real_duplicate_groups:
        for author in group:
            id_group_dict.setdefault(author, list()).append(group)

    authors_duplicates_dict = dict()
    for (author_id, real_duplicate_groups) in id_group_dict.iteritems():
        union_group = set()
        for group in real_duplicate_groups:
            union_group = union_group.union(group)
        authors_duplicates_dict[author_id] = union_group

    return authors_duplicates_dict


def find_closure(authors_duplicates_dict):
    """Find the closure of duplicate authors for each author id.
       Example : {1: [1, 2, 3, 4], 2: [2, 3, 4, 5]} -> {1: [2, 3, 4, 5], 2: [1, 3, 4, 5]}

    Parameters:
        authors_duplicates_dict
            A dictionary of duplicate authors with key: author id and value:
            a list of duplicate author ids
    """
    print "\tFinding close duplicate author set for each author id."
    iteration = 0
    while True:
        print "\t\tIteration " + str(iteration)
        iteration += 1
        if iteration >= 100:
            break
        do_next_recursion = False
        for (author_id, duplicate_group) in authors_duplicates_dict.iteritems():
            changed = False
            final_duplicate_group = set(duplicate_group)
            for _author_id in duplicate_group:
                if duplicate_group != authors_duplicates_dict[_author_id]:
                    changed = True
                    do_next_recursion = True
                    final_duplicate_group = final_duplicate_group.union(authors_duplicates_dict[_author_id])
            if changed:
                authors_duplicates_dict[author_id] = set(final_duplicate_group)
                for _author_id in duplicate_group:
                    authors_duplicates_dict[_author_id] = set(final_duplicate_group)
        if do_next_recursion is False:
            break
    for author_id in authors_duplicates_dict.iterkeys():
        authors_duplicates_dict[author_id].remove(author_id)


def final_refine(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics):
    count = 0
    for author_id in authors_duplicates_dict.iterkeys():
        middle_name = name_instance_dict[id_name_dict[author_id][0]].middle_name.strip()
        if middle_name != '':
            for duplicate_author_id in set(authors_duplicates_dict[author_id]):
                duplicate_author_middle_name = name_instance_dict[id_name_dict[duplicate_author_id][0]].middle_name.strip()
                if duplicate_author_middle_name != '' and SequenceMatcher(None, middle_name, duplicate_author_middle_name).ratio() < 0.5:
                    authors_duplicates_dict[author_id].remove(duplicate_author_id)
                    count += 1
    print "\tRemoving " + str(count) + " author_ids from the final list for middle name mismatch."

    count = 0
    for author_id in authors_duplicates_dict.iterkeys():
        author = name_instance_dict[id_name_dict[author_id][0]]
        first_name = author.first_name.strip()
        if len(first_name) > 1:
            for duplicate_author_id in set(authors_duplicates_dict[author_id]):
                duplicate_author = name_instance_dict[id_name_dict[duplicate_author_id][0]]
                duplicate_author_first_name = duplicate_author.first_name.strip()
                if duplicate_author_first_name == first_name:
                    continue
                if len(duplicate_author_first_name) > 1:
                    if SequenceMatcher(None, first_name, duplicate_author_first_name).ratio() < sequence_matcher_threshold:
                        authors_duplicates_dict[author_id].remove(duplicate_author_id)
                        count += 1
                    elif first_name != duplicate_author_first_name and name_statistics[first_name] > 10 and name_statistics[duplicate_author_first_name] > 10:
                        authors_duplicates_dict[author_id].remove(duplicate_author_id)
                        count += 1 
    print "\tRemoving " + str(count) + " author_ids from the final list for first name mismatch."

    count = 0
    for author_id in authors_duplicates_dict.iterkeys():
        author = name_instance_dict[id_name_dict[author_id][0]]
        first_name = author.first_name.strip()
        if len(first_name) == 1:
            first_name_dict = {}
            for duplicate_author_id in set(authors_duplicates_dict[author_id]):
                duplicate_author = name_instance_dict[id_name_dict[duplicate_author_id][0]]
                duplicate_author_first_name = duplicate_author.first_name.strip()
                first_name_dict.setdefault(duplicate_author_first_name, set()).add(duplicate_author_id)
            if len(first_name_dict) > 1:
                max_length = 0
                for author_set in first_name_dict.itervalues():
                    if len(author_set) > max_length:
                        (max_length, max_author_set) = (len(author_set), author_set)
                if max_length == 1:
                    for duplicate_author_id in set(authors_duplicates_dict[author_id]):
                        authors_duplicates_dict[author_id].remove(duplicate_author_id)
                    count += 1
                else:
                    authors_duplicates_dict[author_id] = max_author_set
                    count += 1
    print "\tRemoving " + str(count) + " author_ids from the final list for first name being shortened."
