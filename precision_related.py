#-*- coding: UTF-8 -*-
from sklearn.preprocessing import normalize
from custom_setting import *
from name import *
from difflib import SequenceMatcher
import re
import itertools

normalized_feature_dict = {}

def is_substr(s1, s2):
    """Does `s1` appear in sequence in `s2`?"""
    return bool(re.search(".*".join(s1), s2)) or bool(re.search(".*".join(s2), s1))

def my_string_match_score(s1, s2):
    elements_s1 = s1.split(" ")
    elements_s2 = s2.split(" ")

    count = 0
    for element1 in elements_s1:
        for element2 in elements_s2:
            if (element1, element2) in nickname_set:
                count += 1
                continue
            if element1[0] != element2[0]:
                continue
            if len(element1) == 1 and len(element2) == 1:
                count += 1
            if len(element1) == 1 and len(element2) != 1:
                count += 1
            if len(element1) != 1 and len(element2) == 1:
                count += 1
            if len(element1) != 1 and len(element2) != 1:
                if SequenceMatcher(None, element1, element2).ratio() > 0.85:
                    count += 1
    if elements_s1[-1] != elements_s2[-1]:
        if SequenceMatcher(None, elements_s1[-1], elements_s2[-1]).ratio() <= 0.85:
            if elements_s1[-1][:-1] == elements_s2[-1][:-1] \
                    or elements_s1[-1][:-1] == elements_s2[-1] \
                    or elements_s1[-1] == elements_s2[-1][:-1]:
                count += 1
    return count



def is_name_reorder(name_instance_A, name_instance_B):
    name_unit_set = set()
    name_unit_set.add(name_instance_A.first_name)
    name_unit_set.add(name_instance_A.middle_name)
    name_unit_set.add(name_instance_A.last_name)
    
    if name_instance_B.first_name in name_unit_set and name_instance_B.middle_name in name_unit_set and name_instance_B.last_name in name_unit_set:
        return True
    else:
        return False

def single_name_comparable(name_instance_A, name_instance_B):
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

    if name_A.replace(' ', '') == name_B.replace(' ', ''):
        return True

    if my_string_match_score(name_instance_A.name, name_instance_B.name) <= 1:
        return False

    # if is_substr(name_A.replace(' ', ''), name_B.replace(' ', '')) and len(name_A) > 10 and len(name_B) > 10:
    #     return True
    if (name_instance_A.first_name, name_instance_B.first_name) not in nickname_set:
        if not is_substr(name_instance_A.initials, name_instance_B.initials):
            return False
    else:
        if not is_substr(name_instance_A.initials[1:], name_instance_B.initials[1:]):
            return False

    # Chris Ding and Cui Ding
    if len(name_instance_A.first_name) > 1 and len(name_instance_B.first_name) > 1:
        if name_instance_A.first_name[0] == name_instance_B.first_name[0]:
            if (name_instance_A.first_name, name_instance_B.first_name) not in nickname_set:
                if (name_instance_A.first_name.find(name_instance_B.first_name) < 0 and name_instance_A.first_name.find(name_instance_B.first_name) < 0) \
                        or (name_instance_A.middle_name == '' and name_instance_B.middle_name == ''):
                    if not name_instance_A.bad_name_flag and not name_instance_B.bad_name_flag:
                        if SequenceMatcher(None, name_instance_A.first_name[1:], name_instance_B.first_name[1:]).ratio() < 0.93:
                            return False
                    else:
                        if SequenceMatcher(None, name_instance_A.first_name[1:], name_instance_B.first_name[1:]).ratio() < 0.5:
                            return False

    # Michael Ia Jordan and Michael Ib jordan
    if len(name_instance_A.middle_name) > 1 and len(name_instance_B.middle_name) > 1:
        if name_instance_A.middle_name[0] == name_instance_B.middle_name[0]:
            if not is_substr(name_instance_A.middle_name.replace(' ', ''), name_instance_B.middle_name.replace(' ', '')):
                if SequenceMatcher(None, name_instance_A.middle_name[1:], name_instance_B.middle_name[1:]).ratio() <= 0.3:
                    return False

    # if len(name_instance_A.last_name) > 1 and len(name_instance_B.last_name) > 1:
    #     if name_instance_A.last_name[0] == name_instance_B.last_name[0]:
    #         if not is_substr(name_instance_A.last_name.replace(' ', ''), name_instance_B.last_name.replace(' ', '')):
    #             if SequenceMatcher(None, name_instance_A.last_name[1:], name_instance_B.last_name[1:]).ratio() < 0.5:
    #                 return False

    if name_instance_A.first_name[0] != name_instance_B.first_name[0]:
        if len(name_instance_B.middle_name) > 0:
            if name_instance_A.first_name[0] == name_instance_B.middle_name[0]:
                if len(name_instance_A.first_name) > 1 and len(name_instance_B.middle_name) > 1:
                    if my_string_match_score(name_instance_A.first_name, name_instance_B.middle_name) == 0:
                        return False
                    # if SequenceMatcher(None, name_instance_A.first_name[1:], name_instance_B.middle_name[1:]).ratio() <= 0.9:
                    #         return False
        if len(name_instance_A.middle_name) > 0:
            if name_instance_B.first_name[0] == name_instance_A.middle_name[0]:
                if len(name_instance_B.first_name) > 1 and len(name_instance_A.middle_name) > 1:
                    if my_string_match_score(name_instance_A.middle_name, name_instance_B.first_name) == 0:
                        # if SequenceMatcher(None, name_instance_A.middle_name[1:], name_instance_B.first_name[1:]).ratio() <= 0.9:
                        return False

    if name_instance_A.last_name != name_instance_B.last_name:
        if SequenceMatcher(None, name_instance_A.last_name[1:], name_instance_B.last_name[1:]).ratio() <= 0.5:
            return False
        # if name_instance_A.middle_name != name_instance_B.middle_name and name_instance_A.first_name != name_instance_B.first_name:
        #     return False

    return True


def __name_comparable(name_instance_A, name_instance_B):
    if single_name_comparable(name_instance_A, name_instance_B):
        return True
    
    name_A = '- '.join([name_instance_A.last_name, name_instance_A.middle_name, name_instance_A.first_name]).strip()
    new_name_instance_A = Name(name_A)
    new_name_instance_A.is_asian = name_instance_A.is_asian
    if single_name_comparable(new_name_instance_A, name_instance_B):
        return True

    name_A = '- '.join([name_instance_A.middle_name, name_instance_A.last_name, name_instance_A.first_name]).strip()
    new_name_instance_A = Name(name_A)
    new_name_instance_A.is_asian = name_instance_A.is_asian
    if single_name_comparable(new_name_instance_A, name_instance_B):
        return True

    name_A = '- '.join([name_instance_A.last_name, name_instance_A.first_name, name_instance_A.middle_name]).strip()
    new_name_instance_A = Name(name_A)
    new_name_instance_A.is_asian = name_instance_A.is_asian
    if single_name_comparable(new_name_instance_A, name_instance_B):
        return True

    name_A = '- '.join([name_instance_A.middle_name, name_instance_A.first_name, name_instance_A.last_name]).strip()
    new_name_instance_A = Name(name_A)
    if new_name_instance_A.name == name_instance_B.name:
        return True

    name_A = '- '.join([name_instance_A.first_name, name_instance_A.last_name, name_instance_A.middle_name]).strip()
    new_name_instance_A = Name(name_A)
    new_name_instance_A.is_asian = name_instance_A.is_asian
    if single_name_comparable(new_name_instance_A, name_instance_B):
        return True

    return False

def name_comparable(name_instance_A, name_instance_B):
    return __name_comparable(name_instance_A, name_instance_B) or __name_comparable(name_instance_B, name_instance_A)
    

def name_group_comparable(group, name_instance_dict, id_name_dict):
    for author_A in group:
        for author_B in group:
            if not name_comparable(name_instance_dict[id_name_dict[author_A][0]], name_instance_dict[id_name_dict[author_B][0]]):
                # print "\t\tConflicted name group: " + id_name_dict[author_A][0] + '\tv.s.\t' + id_name_dict[author_B][0]
                return False
    return True


def compute_similarity_score(author_A, author_B, metapaths):
    if author_A not in normalized_feature_dict:
        feature_A = (metapaths.AP.getrow(author_A), metapaths.APA.getrow(author_A), \
            metapaths.AV.getrow(author_A), metapaths.AVA.getrow(author_A), \
            metapaths.AW.getrow(author_A), metapaths.AK.getrow(author_A))
        normalized_feature_A = (
            normalize(feature_A[0], norm='l2', axis=1),
            normalize(feature_A[1], norm='l2', axis=1),
            normalize(feature_A[2], norm='l2', axis=1),
            normalize(feature_A[3], norm='l2', axis=1),
            normalize(feature_A[4], norm='l2', axis=1),
            normalize(feature_A[5], norm='l2', axis=1))
        normalized_feature_dict[author_A] = normalized_feature_A
    else:
        normalized_feature_A = normalized_feature_dict[author_A]

    if author_B not in normalized_feature_dict:
        feature_B = (metapaths.AP.getrow(author_B), metapaths.APA.getrow(author_B), \
            metapaths.AV.getrow(author_B), metapaths.AVA.getrow(author_B), \
            metapaths.AW.getrow(author_B), metapaths.AK.getrow(author_B))
        normalized_feature_B = (
            normalize(feature_B[0], norm='l2', axis=1),
            normalize(feature_B[1], norm='l2', axis=1),
            normalize(feature_B[2], norm='l2', axis=1),
            normalize(feature_B[3], norm='l2', axis=1),
            normalize(feature_B[4], norm='l2', axis=1),
            normalize(feature_B[5], norm='l2', axis=1))
        normalized_feature_dict[author_B] = normalized_feature_B
    else:
        normalized_feature_B = normalized_feature_dict[author_B]

    similarity = (1000000 * normalized_feature_A[0].multiply(normalized_feature_B[0]).sum(), #same paper
             100000 * normalized_feature_A[1].multiply(normalized_feature_B[1]).sum(), #coauthor
             100000 * normalized_feature_A[2].multiply(normalized_feature_B[2]).sum(), #same venue
             1000 * normalized_feature_A[3].multiply(normalized_feature_B[3]).sum(), #covenue
             10 * normalized_feature_A[3].multiply(normalized_feature_B[1]).sum(),
             10 * normalized_feature_A[1].multiply(normalized_feature_B[3]).sum(),
             100 * normalized_feature_A[4].multiply(normalized_feature_B[4]).sum(),
             100000 * normalized_feature_A[5].multiply(normalized_feature_B[5]).sum(), merge_threshold)

    return similarity


def local_clustering(potential_duplicate_groups, author_paper_stat, name_instance_dict, id_name_dict, metapaths):
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
    statistic = [0] * 9
    real_duplicate_groups = set()

    normalized_feature_dict = {}
    similarity_dict = {}

    for potential_duplicate_group in potential_duplicate_groups:  
        if count % 20000 == 0:
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

        similarity = compute_similarity_score(author_A, author_B, metapaths)
        if max(similarity) >= merge_threshold:
            real_duplicate_groups.add(potential_duplicate_group)
            statistic[similarity.index(max(similarity))] += 1

        similarity_dict[potential_duplicate_group] = max(similarity)

    return (real_duplicate_groups, similarity_dict)


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


def refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, similarity_dict, metapaths):
    for author_id in authors_duplicates_dict.iterkeys():
        if author_id in authors_duplicates_dict[author_id]:
            authors_duplicates_dict[author_id].remove(author_id)

    count = 0
    for author_id in authors_duplicates_dict.iterkeys():
        for duplicate_author_id in set(authors_duplicates_dict[author_id]):
            if not name_comparable(name_instance_dict[id_name_dict[author_id][0]], \
                    name_instance_dict[id_name_dict[duplicate_author_id][0]]):
                authors_duplicates_dict[author_id].remove(duplicate_author_id)
                if author_id in authors_duplicates_dict[duplicate_author_id]:
                    authors_duplicates_dict[duplicate_author_id].remove(author_id)
                count += 1
    print "\tRemoving " + str(count) + " author_ids from name comparison."

    conflict_ids = find_conflict_name(authors_duplicates_dict, name_instance_dict, id_name_dict)
    max_similarity_dict = {}
    for author_id in conflict_ids:
        pool = authors_duplicates_dict[author_id]
        for candi in pool:
            if tuple(sorted((author_id, candi))) not in similarity_dict:
                similarity_dict[tuple(sorted((author_id, candi)))] = max(compute_similarity_score(author_id, candi, metapaths))
        max_similarity_dict[author_id] = max([similarity_dict[tuple(sorted((author_id, candi)))] for candi in authors_duplicates_dict[author_id]])

    conflict_ids = sorted(conflict_ids, key=lambda candi: -max_similarity_dict[candi])
    count = 0
    for author_id in conflict_ids:
        pool = authors_duplicates_dict[author_id]
        pool = sorted(pool, key=lambda candi: -similarity_dict[tuple(sorted((author_id, candi)))])
        group = [author_id]
        for candidate in pool:
            group.append(candidate)
            if not name_group_comparable(group, name_instance_dict, id_name_dict):
                group.pop()
        for id in authors_duplicates_dict[author_id]:
            if id not in group and author_id in authors_duplicates_dict[id]:
                authors_duplicates_dict[id].remove(author_id)
        authors_duplicates_dict[author_id] = set(group)
        count += 1
        if count % 100 == 0:
            print "\tFinish analysing " \
                + str(float(count)/len(conflict_ids)*100) \
                + "% (" + str(count) + "/" + str(len(conflict_ids)) \
                + ") conflict_ids."

    for author_id in authors_duplicates_dict.iterkeys():
        if author_id in authors_duplicates_dict[author_id]:
            authors_duplicates_dict[author_id].remove(author_id)


def final_filter(authors_duplicates_dict, name_instance_dict, id_name_dict):
    count = 0
    for author_id in authors_duplicates_dict.iterkeys():
        if len(authors_duplicates_dict[author_id]) == 1:
            name_instance_A = name_instance_dict[id_name_dict[author_id][0]]
            name_A = id_name_dict[author_id][0]
            elements_A = name_A.split(' ')
            #remove  A Dgh EF and Abc EF pairs
            to_remove_set = set()
            for id in authors_duplicates_dict[author_id]:
                name_instance_B = name_instance_dict[id_name_dict[id][0]]
                name_B = id_name_dict[id][0]
                elements_B = name_B.split(' ')
                if len(elements_A) > 2 and len(elements_A[0]) == 1 and len(elements_A[1]) > 1:
                    if len(elements_B[0]) > 1 and len(elements_B) == 2 and elements_A[0][0] == elements_B[0][0] and elements_A[1][0] != elements_B[0][0]:
                        to_remove_set.add(id)
                        count += 1
                        print '\t\tRemoving ' + name_B + ' from duplicates_set of ' + name_A
                elif len(elements_B) > 2 and len(elements_B[0]) == 1 and len(elements_B[1]) > 1:
                    if len(elements_A[0]) > 1 and len(elements_A) == 2 and elements_B[0][0] == elements_A[0][0] and elements_B[1][0] != elements_A[0][0]:
                        to_remove_set.add(id)
                        count += 1
                        print '\t\tRemoving ' + name_B + ' from duplicates_set of ' + name_A

            for id in to_remove_set:
                authors_duplicates_dict[author_id].remove(id)
    print "\tFinish removing " + str(float(count)) \
                + " unconfident names."