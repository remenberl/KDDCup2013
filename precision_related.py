#-*- coding: UTF-8 -*-
from sklearn.preprocessing import normalize
from custom_setting import *
from name import *
from difflib import SequenceMatcher
import re
import itertools

def name_comparable(name_instance_A, name_instance_B):
    name_A = name_instance_A.name
    name_B = name_instance_B.name

    if name_instance_A.is_asian and name_instance_B.is_asian:
        # Han Liu and Huan Liu
        if name_instance_A.middle_name == '' and name_instance_B.middle_name == '':
            if len(name_instance_A.first_name) > 1 and len(name_instance_B.first_name) > 1:
                if name_instance_A.first_name != name_instance_B.first_name:
                    return False
        # Han Liu  and H. L. Liu
        if len(name_instance_A.first_name) == 1 and len(name_instance_A.middle_name) == 1:
            if not is_substr(name_A.replace(' ', ''), name_B):
                return False
        if len(name_instance_B.first_name) == 1 and len(name_instance_B.middle_name) == 1:
            if not is_substr(name_A, name_B.replace(' ', '')):
                return False
        # Lin Yu, Lin Yi
        if name_instance_A.last_name != name_instance_B.last_name:
            return False

    if name_B.find(name_A.replace(' ', '')) >= 0 or name_A.find(name_B.replace(' ', '')) >= 0:
        return True

    if not is_substr(name_instance_A.initials, name_instance_B.initials):
        return False

    # Chris Ding and Cui Ding
    if len(name_instance_A.first_name) > 1 and len(name_instance_B.first_name) > 1:
        if name_instance_A.first_name[0] == name_instance_B.first_name[0]:
            if (name_instance_A.first_name, name_instance_B.first_name) not in nickname_set:
                if SequenceMatcher(None, name_instance_A.first_name[1:], name_instance_B.first_name[1:]).ratio() != 1:
                    return False

    # Michael Ia Jordan and Michael Ib jordan
    if len(name_instance_A.middle_name) > 1 and len(name_instance_B.middle_name) > 1:
        if name_instance_A.middle_name[0] == name_instance_B.middle_name[0]:
            if SequenceMatcher(None, name_instance_A.middle_name[1:], name_instance_B.middle_name[1:]).ratio() <= 0.3:
                return False

    return True


def name_group_comparable(group, name_instance_dict, id_name_dict):
    for author_A in group:
        for author_B in group:
            if not name_comparable(name_instance_dict[id_name_dict[author_A][0]], name_instance_dict[id_name_dict[author_B][0]]):
                return False
    return True


def local_clustering(potential_duplicate_groups, author_paper_stat, name_instance_dict, id_name_dict, coauthor_matrix, covenue_matrix, author_word_matrix):
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
    count = 0
    statistic = [0] * 6
    real_duplicate_groups = set()

    normalized_feature_dict = {}

    for potential_duplicate_group in potential_duplicate_groups:  
        if count % 5000 == 0:
            print "\tFinish analysing " \
                + str(float(count)/len(potential_duplicate_groups)*100) \
                + "% (" + str(count) + "/" + str(len(potential_duplicate_groups)) \
                + ") possible duplicate groups."
            print "\tStatistic about merges based on different features: " + str(statistic)
        count += 1

        author_A = potential_duplicate_group[0]
        author_B = potential_duplicate_group[1]

        if author_A not in author_paper_stat or author_B not in author_paper_stat:
            continue


        if not name_comparable(name_instance_dict[id_name_dict[author_A][0]], name_instance_dict[id_name_dict[author_B][0]]):
            continue


        if author_A not in normalized_feature_dict:
            feature_A = (coauthor_matrix.getrow(author_A), covenue_matrix.getrow(author_A), author_word_matrix.getrow(author_A))
            normalized_feature_A = (
                normalize(feature_A[0], norm='l2', axis=1),
                normalize(feature_A[1], norm='l2', axis=1),
                normalize(feature_A[2], norm='l2', axis=1))
            normalized_feature_dict[author_A] = normalized_feature_A
        else:
            normalized_feature_A = normalized_feature_dict[author_A]

        if author_B not in normalized_feature_dict:
            feature_B = (coauthor_matrix.getrow(author_B), covenue_matrix.getrow(author_B), author_word_matrix.getrow(author_B))
            normalized_feature_B = (
                normalize(feature_B[0], norm='l2', axis=1),
                normalize(feature_B[1], norm='l2', axis=1),
                normalize(feature_B[2], norm='l2', axis=1))
            normalized_feature_dict[author_B] = normalized_feature_B
        else:
            normalized_feature_B = normalized_feature_dict[author_B]

        similarity = (normalized_feature_A[0].multiply(normalized_feature_B[0]).sum(),
                     normalized_feature_A[1].multiply(normalized_feature_B[1]).sum(),
                     normalized_feature_A[0].multiply(normalized_feature_B[1]).sum(),
                     normalized_feature_A[1].multiply(normalized_feature_B[0]).sum(),
                     normalized_feature_A[2].multiply(normalized_feature_B[2]).sum())

        # ((normalized_feature_A[0] * normalized_feature_B[0].transpose())[0, 0],
        #              (normalized_feature_A[1] * normalized_feature_B[1].transpose())[0, 0],
        #              (normalized_feature_A[0] * normalized_feature_B[1].transpose())[0, 0],
        #              (normalized_feature_A[1] * normalized_feature_B[0].transpose())[0, 0],
        #              (normalized_feature_A[2] * normalized_feature_B[2].transpose())[0, 0])
        
        if max(similarity) > merge_threshold:
            real_duplicate_groups.add(potential_duplicate_group)
            statistic[similarity.index(max(similarity))] += 1


    return real_duplicate_groups


def merge_local_clusters(real_duplicate_groups, id_name_dict):
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

    for author_id in id_name_dict.iterkeys():
        authors_duplicates_dict.setdefault(author_id, set()).add(author_id)

    return authors_duplicates_dict


def find_conflict_name(authors_duplicates_dict, name_instance_dict, id_name_dict):
    conflict_ids = set()
    for (author_id, duplicate_group) in authors_duplicates_dict.iteritems():
        if not name_group_comparable(duplicate_group, name_instance_dict, id_name_dict):
            conflict_ids.add(author_id)
    return conflict_ids


def find_closure(authors_duplicates_dict):
    """Find the closure of duplicate authors for each author id.
       Example : {1: [1, 2, 3, 4], 2: [2, 3, 4, 5]} -> {1: [2, 3, 4, 5], 2: [1, 3, 4, 5]}

    Parameters:
        authors_duplicates_dict
            A dictionary of duplicate authors with key: author id and value:
            a list of duplicate author ids
    """
    print "\tFinding close duplicate author set for each author id."
    for author_id in authors_duplicates_dict.iterkeys():
        authors_duplicates_dict[author_id].add(author_id)

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


def is_substr(s1, s2):
    """Does `s1` appear in sequence in `s2`?"""
    return bool(re.search(".*".join(s1), s2)) or bool(re.search(".*".join(s2), s1))

def final_refine(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics):
    for author_id in authors_duplicates_dict.iterkeys():
        if author_id in authors_duplicates_dict[author_id]:
            authors_duplicates_dict[author_id].remove(author_id)

    count = 0
    for author_id in authors_duplicates_dict.iterkeys():
        for duplicate_author_id in set(authors_duplicates_dict[author_id]):
            if not name_comparable(name_instance_dict[id_name_dict[author_id][0]], \
                    name_instance_dict[id_name_dict[duplicate_author_id][0]]):
                authors_duplicates_dict[author_id].remove(duplicate_author_id)
                count += 1
    print "\tRemoving " + str(count) + " author_ids from name comparison."

    conflict_ids = find_conflict_name(authors_duplicates_dict, name_instance_dict, id_name_dict)

    count = 0
    for author_id in conflict_ids:
        pool = authors_duplicates_dict[author_id]
        max_size = 1
        max_group = list()
        max_size_history = list()
        discovered = set()
        group = [author_id]
        current_size = 1
        itera = 1
        while len(group) >= 1 and len(group) < len(pool) + 1: 
            itera += 1
            if itera == 10:
                break
            for candidate in pool:
                if candidate not in group and tuple(group) + (candidate,) not in discovered:
                    discovered.add(tuple(group) + (candidate,))
                    group.append(candidate)
                    current_size += 1
                    if not name_group_comparable(group, name_instance_dict, id_name_dict):
                        group.pop()
                        current_size -= 1
                        break
                    else:
                        if current_size > max_size:
                            max_size = current_size
                            max_group = group
                        break
            else:
                max_size_history.append(current_size)
                group.pop()
                current_size -= 1

        if max_size_history.count(max_size) >= 2:
            pass
        #     for id in authors_duplicates_dict[author_id]:
        #         if author_id in authors_duplicates_dict[id]:
        #             authors_duplicates_dict[id].remove(author_id)
        #     authors_duplicates_dict[author_id] = set()
        else:
            authors_duplicates_dict[author_id] = set(max_group)
            for id in authors_duplicates_dict[author_id]:
                if id not in max_group and author_id in authors_duplicates_dict[id]:
                    authors_duplicates_dict[id].remove(author_id)
        
        count += 1
        if count % 100 == 0:
            print "\tFinish analysing " \
                + str(float(count)/len(conflict_ids)*100) \
                + "% (" + str(count) + "/" + str(len(conflict_ids)) \
                + ") conflict_ids."

    for author_id in authors_duplicates_dict.iterkeys():
        if author_id in authors_duplicates_dict[author_id]:
            authors_duplicates_dict[author_id].remove(author_id)

