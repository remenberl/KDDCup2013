#-*- coding: UTF-8 -*-
from SOAPpy import SOAPServer
from sklearn.preprocessing import normalize
from difflib import SequenceMatcher
from name import *
from soap_service import *
from custom_setting import *
from io import *


def match_names(name_instance_dict):
    """Find similar names for each name in name_instance_dict.

    Parameters:
        name_instance_dict:
            A dictionary with key: author's name string and value:
            name instance. Note that the author's name is clean after
            instantiation of the Name class.
    """
    for (author_name, name_instance) in name_instance_dict.iteritems():
        alternatives = name_instance.get_alternatives()
        for alternative in alternatives:
            if alternative in name_instance_dict:
                # Add author_ids into the similar_author_ids
                # of the name's alternative.
                for id in name_instance.author_ids:
                    name_instance_dict[alternative].add_similar_author_id(id)
                # Add alternative's author_ids into the similar_author_ids
                # of the current name.
                for id in name_instance_dict[alternative].author_ids:
                    name_instance_dict[author_name].add_similar_author_id(id)

    for (author_name1, name_instance1) in name_instance_dict.iteritems():
        for (author_name2, name_instance2) in name_instance_dict.iteritems():
            if SequenceMatcher(None, author_name1, author_name2).real_quick_ratio() >= sequence_matcher_threshold:
                if SequenceMatcher(None, author_name1, author_name2).real_quick_ratio() >= sequence_matcher_threshold:
                    for id in name_instance1.author_ids:
                        name_instance2.add_similar_author_id(id)
                    for id in name_instance2.author_ids:
                        name_instance1.add_similar_author_id(id)


def create_groups(name_instance_dict):
    """Create potential duplicate groups for undistinct algorithm to analyse.

    Parameters:
        name_instance_dict:
            A dictionary with key: author's name string and value:
            name instance. Note that the author's name is clean after
            initialization of the Name class.

    Returns:
        A set containing lots of tuples describing the potential duplicate group.
    """
    groups = set()
    for (author_name, name_instance) in name_instance_dict.iteritems():
        groups.add(tuple(name_instance.author_ids))
        groups.add(tuple(name_instance.similar_author_ids))
    return groups


def distinct(possible_duplicate_groups, coauthor_matrix):
    """Detect duplicate groups based on coauthor relationship between authors.

    Parameters:
        possible_duplicate_groups:
            A set containing lots of tuples describing the potential duplicate group.
        coauthor_matrix:
            A sparse matrix with row: author_id and column: author_id.
            It is obtained from author_paper_matrix.

    Returns:
        duplicate_groups:
            A set containing lots of tuples describing the duplicate group.
    """
    duplicate_groups = set()
    print "In total " + str(len(possible_duplicate_groups)) + " groups:"
    count = 0
    for group in possible_duplicate_groups:
        count += 1
        if count % 100 == 0:
            print "Finish analysing " \
                + str(float(count)/len(possible_duplicate_groups)*100) \
                + "% (" + str(count) + "/" + str(len(possible_duplicate_groups)) \
                + ") possible duplicate groups."
        # If there is only one author_id in the group, pass
        if len(group) == 1:
            duplicate_groups.add(group)
            continue

        similarity_dict = dict()
        author_feature_dict = dict()
        normalized_author_feature_dict = dict()
        # Treat coauthors for a particular author as features and normalize it
        for author in group:
            author_feature_dict[(author,)] = coauthor_matrix.getrow(author)
            normalized_author_feature_dict[(author,)] = normalize(
                author_feature_dict[(author,)], norm='l2', axis=1)
        # Compute Cosine similarity between every pair of potential duplicate authors in the group
        for author_A in group:
            for author_B in group:
                if author_A < author_B:
                    similarity_dict[((author_A,), (author_B,))] \
                        = (normalized_author_feature_dict[(author_A,)]
                            * normalized_author_feature_dict[(author_B,)].transpose())[0, 0]

        while True:
            max_similarity = 0
            max_pair = ()
            # Find the author partition pair with largest similarity
            # and it should be larger than then the threshold
            for (author_group_pair, similarity) in similarity_dict.iteritems():
                (max_similarity, max_pair) = (similarity, author_group_pair) \
                    if similarity > merge_threshold else (max_similarity, max_pair)

            # If we cannot find such an author group pair,
            #   output the current duplicate authors in the whole group,
            # else
            #   we merge this pair
            if max_similarity == 0:
                for author_group in author_feature_dict.iterkeys():
                    duplicate_groups.add(author_group)
                break
            else:
                # Compute the new feature and normalize it for the merged author partition pair
                new_feature = author_feature_dict[max_pair[0]] + author_feature_dict[max_pair[1]]
                new_author_group = max_pair[0] + max_pair[1]
                author_feature_dict[new_author_group] = new_feature
                normalized_author_feature_dict[new_author_group]\
                    = normalize(author_feature_dict[new_author_group], norm='l2', axis=1)

                # Remove individual author partition in the new merged author partition
                del author_feature_dict[max_pair[0]]
                del author_feature_dict[max_pair[1]]
                rm_list = list()
                for author_group_pair in similarity_dict.iterkeys():
                    if author_group_pair[0] == max_pair[1] \
                            or author_group_pair[1] == max_pair[1] \
                            or author_group_pair[0] == max_pair[0] \
                            or author_group_pair[1] == max_pair[0]:
                        rm_list.append(author_group_pair)
                for author_group_pair in rm_list:
                    del similarity_dict[author_group_pair]
                # Compute new similarity between this new partition
                # with the rest existing partitions
                for author_group in author_feature_dict.iterkeys():
                    if author_group is not new_author_group:
                        similarity_dict[(author_group, new_author_group)] \
                            = (normalized_author_feature_dict[author_group]
                                * normalized_author_feature_dict[new_author_group].transpose())[0, 0]
    return duplicate_groups


def refine_duplicate_groups(duplicate_groups, coauthor_matrix):
    """Refine the duplicate authors for each author id.

    Parameters:
        duplicate_groups:
            A set of groups which contain duplicate author_ids separately.
        coauthor_matrix:
            A sparse matrix with row: author_id and column: author_id.
            It is obtained from author_paper_matrix.

    Returns:
        A dictionary of duplicate authors with key: author id and value:
        a list of duplicate author ids
    """
    duplicate_ids = dict()
    count = 0
    length = len(duplicate_groups)
    for group in duplicate_groups:
        for author in group:
            group_bak = set(group)
            group_bak.remove(author)
            duplicate_ids.setdefault(author, list()).append(group_bak)

        count += 1
        if count % 1000 == 0:
            print "Finish mapping each author to duplicate authors from " \
                + str(float(count)/length*100) \
                + "% (" + str(count) + "/" + str(length) \
                + ") duplicate groups."

    authors_duplicates_dict = dict()
    for (author_id, duplicate_groups) in duplicate_ids.iteritems():
        duplicate_group = set()
        for group in duplicate_groups:
            duplicate_group = duplicate_group.union(group)
        authors_duplicates_dict[author_id] = duplicate_group

    #####################################################
    # Further improvements:
    # Get better idea about refining the duplicate_groups for
    # each author_id to be exactly one set.
    # Currently, there are more than one groups because:
    # We generate potential groups based on author's name.
    # So for "Michael Jordan" we have a group and for "M.I. Jordan" we have another.
    # And for both groups we have some overlapping author_ids.

    return authors_duplicates_dict


if __name__ == '__main__':
    mode = raw_input("Type in number to choose running mode:\n" +
                     "(0: Generate Submission File, 1: Work as SOAP server)\n")
    if int(mode) == 0:
        (name_instance_dict, id_name_dict, name_statistics,
            author_paper_matrix, coauthor_matrix) = load_files()
        match_names(name_instance_dict)
        possible_duplicate_groups = create_groups(name_instance_dict)
        duplicate_groups = distinct(possible_duplicate_groups, coauthor_matrix)
        authors_duplicates_dict = refine_duplicate_groups(duplicate_groups, coauthor_matrix)
        save_result(authors_duplicates_dict, name_instance_dict, id_name_dict)
    elif int(mode) == 1:
        (name_instance_dict, id_name_dict, name_statistics,
            author_paper_matrix, coauthor_matrix) = load_files()
        match_names(name_instance_dict)

        server = SOAPServer((server_soap_address, server_port))
        soap_service = SOAPService(name_instance_dict, id_name_dict)
        server.registerObject(soap_service)
        print "SOAP service starts working."
        server.serve_forever()
