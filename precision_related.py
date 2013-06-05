#-*- coding: UTF-8 -*-
from sklearn.preprocessing import normalize
from custom_setting import *
from name import *
from difflib import SequenceMatcher
import re
import itertools
import fuzzy

normalized_feature_dict = {}
soundex = fuzzy.Soundex(4)

def is_substr(s1, s2):
    """Does `s1` appear in sequence in `s2`?"""
    return bool(re.search(".*".join(s1), s2)) or bool(re.search(".*".join(s2), s1))

def my_string_match_score(s1, s2, name_statistics, is_asian=False):
    elements_s1 = s1.split(" ")
    elements_s2 = s2.split(" ")

    count = 0
    for element1 in elements_s1:
        for element2 in elements_s2:
            if (element1, element2) in nickname_set or (element1, element2) in nickname_initials_set:
                count += 1
                continue
            if element1 == '' or element2 == '':
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
                if is_asian:
                    if SequenceMatcher(None, element1, element2).ratio() > 0.90:
                        if element1 == element2 and element1 in name_statistics and name_statistics[element1] <= 10:
                            count += 5
                        else:
                            count += 1
                else:
                    element1 = element1.lower()
                    element2 = element2.lower()
                    ldis = SequenceMatcher(None, element1, element2).ratio()
                    if ldis > 0.85 or \
                            (ldis > 0.80 and abs(int(soundex(element1)[1:]) - int(soundex(element2)[1:])) <= 2):
                        if element1 == element2 and element1 in name_statistics and name_statistics[element1] <= 10:
                            count += 5
                        else:
                            count += 1

    if elements_s1[-1] != elements_s2[-1]:
        if is_asian:
            if SequenceMatcher(None, elements_s1[-1], elements_s2[-1]).ratio() <= 0.90:
                if elements_s1[-1][:-1] == elements_s2[-1][:-1] \
                        or elements_s1[-1][:-1] == elements_s2[-1] \
                        or elements_s1[-1] == elements_s2[-1][:-1]:
                    count += 1
        else:
            element1 = elements_s1[-1].lower()
            element2 = elements_s2[-1].lower()
            ldis = SequenceMatcher(None, element1, element2).ratio()
            if ldis <= 0.85 and \
                        (ldis <= 0.80 or abs(int(soundex(element1)[1:]) - int(soundex(element2)[1:])) > 2):
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

def single_name_comparable(name_instance_A, name_instance_B, name_statistics):
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

    score = my_string_match_score(name_instance_A.name, name_instance_B.name, name_statistics, name_instance_A.is_asian or name_instance_B.is_asian)
    if score <= 1:
        return False

    if score >= 10:
        return True
    # if is_substr(name_A.replace(' ', ''), name_B.replace(' ', '')) and len(name_A) > 10 and len(name_B) > 10:
    #     return True
    if (name_instance_A.first_name, name_instance_B.first_name) not in nickname_set and (name_instance_A.first_name, name_instance_B.first_name) not in nickname_initials_set:
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
                        first_name_1 = name_instance_A.first_name.lower()
                        first_name_2 = name_instance_B.first_name.lower()
                        if name_instance_A.is_asian or name_instance_B.is_asian:
                            if SequenceMatcher(None, name_instance_A.first_name[1:], name_instance_B.first_name[1:]).ratio() < 0.93:
                                return False
                        else:
                            ldis = SequenceMatcher(None, name_instance_A.first_name[1:], name_instance_B.first_name[1:]).ratio() 
                            if ldis < 0.93 and\
                                    (ldis < 0.80 or soundex(first_name_1) != soundex(first_name_2)):
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
    if name_instance_A.first_name[0] != name_instance_B.first_name[0] and (name_instance_A.first_name, name_instance_B.first_name) not in nickname_initials_set:
        if len(name_instance_B.middle_name) > 0:
            if name_instance_A.first_name[0] == name_instance_B.middle_name[0]:
                if len(name_instance_A.first_name) > 1 and len(name_instance_B.middle_name) > 1:
                    if my_string_match_score(name_instance_A.first_name, name_instance_B.middle_name, name_statistics) == 0:
                        return False
            else:
                if my_string_match_score(name_instance_A.name + ' ' + name_instance_A.middle_name, \
                        name_instance_B.first_name + ' ' + name_instance_B.first_name, name_statistics) == 0:
                        # if SequenceMatcher(None, name_instance_A.middle_name[1:], name_instance_B.first_name[1:]).ratio() <= 0.9:
                    return False
                    # if SequenceMatcher(None, name_instance_A.first_name[1:], name_instance_B.middle_name[1:]).ratio() <= 0.9:
                    #         return False
        if len(name_instance_A.middle_name) > 0:
            if name_instance_B.first_name[0] == name_instance_A.middle_name[0]:
                if len(name_instance_B.first_name) > 1 and len(name_instance_A.middle_name) > 1:
                    if my_string_match_score(name_instance_A.middle_name, name_instance_B.first_name, name_statistics) == 0:
                        # if SequenceMatcher(None, name_instance_A.middle_name[1:], name_instance_B.first_name[1:]).ratio() <= 0.9:
                        return False
            else:
                if my_string_match_score(name_instance_A.name + ' ' + name_instance_A.middle_name, \
                        name_instance_B.first_name + ' ' + name_instance_B.first_name, name_statistics) == 0:
                        # if SequenceMatcher(None, name_instance_A.middle_name[1:], name_instance_B.first_name[1:]).ratio() <= 0.9:
                    return False

    if name_instance_A.last_name != name_instance_B.last_name:
        if SequenceMatcher(None, name_instance_A.last_name[1:], name_instance_B.last_name[1:]).ratio() <= 0.5:
            return False
        # if name_instance_A.middle_name != name_instance_B.middle_name and name_instance_A.first_name != name_instance_B.first_name:
        #     return False
    return True


def __name_comparable(name_instance_A, name_instance_B, name_statistics, strict_mode=True):
    if single_name_comparable(name_instance_A, name_instance_B, name_statistics):
        return True
    
    name_A = '- '.join([name_instance_A.last_name, name_instance_A.middle_name, name_instance_A.first_name]).strip()
    new_name_instance_A = Name(name_A)
    new_name_instance_A.is_asian = name_instance_A.is_asian
    if single_name_comparable(new_name_instance_A, name_instance_B, name_statistics):
        return True

    name_A = '- '.join([name_instance_A.middle_name, name_instance_A.last_name, name_instance_A.first_name]).strip()
    new_name_instance_A = Name(name_A)
    new_name_instance_A.is_asian = name_instance_A.is_asian
    if single_name_comparable(new_name_instance_A, name_instance_B, name_statistics):
        return True

    name_A = '- '.join([name_instance_A.last_name, name_instance_A.first_name, name_instance_A.middle_name]).strip()
    new_name_instance_A = Name(name_A)
    new_name_instance_A.is_asian = name_instance_A.is_asian
    if single_name_comparable(new_name_instance_A, name_instance_B, name_statistics):
        return True

    name_A = '- '.join([name_instance_A.middle_name, name_instance_A.first_name, name_instance_A.last_name]).strip()
    new_name_instance_A = Name(name_A)
    new_name_instance_A.is_asian = name_instance_A.is_asian
    if strict_mode:
        if new_name_instance_A.name == name_instance_B.name:
            return True
    else:
        if single_name_comparable(new_name_instance_A, name_instance_B, name_statistics):
            return True

    name_A = '- '.join([name_instance_A.first_name, name_instance_A.last_name, name_instance_A.middle_name]).strip()
    new_name_instance_A = Name(name_A)
    new_name_instance_A.is_asian = name_instance_A.is_asian
    if single_name_comparable(new_name_instance_A, name_instance_B, name_statistics):
        return True

    return False

def name_comparable(name_instance_A, name_instance_B, name_statistics, strict_mode=True):
    return __name_comparable(name_instance_A, name_instance_B, name_statistics, strict_mode) or __name_comparable(name_instance_B, name_instance_A, name_statistics, strict_mode)
    

def name_group_comparable(group, name_instance_dict, id_name_dict, name_statistics):
    for author_A in group:
        for author_B in group:
            if not name_comparable(name_instance_dict[id_name_dict[author_A][0]], name_instance_dict[id_name_dict[author_B][0]], name_statistics, False):
                # print "\t\tConflicted name group: " + id_name_dict[author_A][0] + '\tv.s.\t' + id_name_dict[author_B][0]
                return False
    return True


def compute_similarity_score(author_A, author_B, metapaths):
    if author_A not in normalized_feature_dict:
        feature_A = (metapaths.AP.getrow(author_A), metapaths.APA.getrow(author_A), \
            metapaths.APV.getrow(author_A), metapaths.APVPA.getrow(author_A), \
            metapaths.APW.getrow(author_A), metapaths.APK.getrow(author_A), \
            metapaths.AO.getrow(author_A), metapaths.APAPA.getrow(author_A), \
            metapaths.APKPA.getrow(author_A), metapaths.APAPV.getrow(author_A), \
            metapaths.AY.getrow(author_A))
        normalized_feature_A = (
            normalize(feature_A[0], norm='l2', axis=1),
            normalize(feature_A[1], norm='l2', axis=1),
            normalize(feature_A[2], norm='l2', axis=1),
            normalize(feature_A[3], norm='l2', axis=1),
            normalize(feature_A[4], norm='l2', axis=1),
            normalize(feature_A[5], norm='l2', axis=1),
            normalize(feature_A[6], norm='l2', axis=1),
            normalize(feature_A[7], norm='l2', axis=1),
            normalize(feature_A[8], norm='l2', axis=1),
            normalize(feature_A[9], norm='l2', axis=1),
            normalize(feature_A[10], norm='l2', axis=1))
        normalized_feature_dict[author_A] = normalized_feature_A
    else:
        normalized_feature_A = normalized_feature_dict[author_A]

    if author_B not in normalized_feature_dict:
        feature_B = (metapaths.AP.getrow(author_B), metapaths.APA.getrow(author_B), \
            metapaths.APV.getrow(author_B), metapaths.APVPA.getrow(author_B), \
            metapaths.APW.getrow(author_B), metapaths.APK.getrow(author_B), \
            metapaths.AO.getrow(author_B), metapaths.APAPA.getrow(author_B), \
            metapaths.APKPA.getrow(author_B), metapaths.APAPV.getrow(author_B), \
            metapaths.AY.getrow(author_B))
        normalized_feature_B = (
            normalize(feature_B[0], norm='l2', axis=1),
            normalize(feature_B[1], norm='l2', axis=1),
            normalize(feature_B[2], norm='l2', axis=1),
            normalize(feature_B[3], norm='l2', axis=1),
            normalize(feature_B[4], norm='l2', axis=1),
            normalize(feature_B[5], norm='l2', axis=1),
            normalize(feature_B[6], norm='l2', axis=1),
            normalize(feature_B[7], norm='l2', axis=1),
            normalize(feature_B[8], norm='l2', axis=1),
            normalize(feature_B[9], norm='l2', axis=1),
            normalize(feature_B[10], norm='l2', axis=1))
        normalized_feature_dict[author_B] = normalized_feature_B
    else:
        normalized_feature_B = normalized_feature_dict[author_B]

    similarity = (1000000 * normalized_feature_A[0].multiply(normalized_feature_B[0]).sum(), #same paper
             100000 * normalized_feature_A[1].multiply(normalized_feature_B[1]).sum(), #APA
             100000 * normalized_feature_A[2].multiply(normalized_feature_B[2]).sum(), #AV
             1000 * normalized_feature_A[3].multiply(normalized_feature_B[3]).sum(), #AVA
             1000 * normalized_feature_A[3].multiply(normalized_feature_B[7]).sum(),
             1000 * normalized_feature_A[7].multiply(normalized_feature_B[3]).sum(),
             100 * normalized_feature_A[4].multiply(normalized_feature_B[4]).sum(),
             100000 * normalized_feature_A[5].multiply(normalized_feature_B[5]).sum(), 
             10000000 * normalized_feature_A[6].multiply(normalized_feature_B[6]).sum(),
             1000 * normalized_feature_A[7].multiply(normalized_feature_B[7]).sum(), #APAPA
             1000 * normalized_feature_A[8].multiply(normalized_feature_B[8]).sum(), #AKA
             1000 * normalized_feature_A[9].multiply(normalized_feature_B[9]).sum(), #APAPV
             1 * normalized_feature_A[10].multiply(normalized_feature_B[10]).sum(), merge_threshold)

    return similarity

def is_simple_name(name):
    elements = name.split(' ')
    for element in elements[:-1]:
        if len(element) != 1:
            break
    else:
        return True
    return False

def local_clustering(potential_duplicate_groups, author_paper_stat, name_instance_dict, id_name_dict, name_statistics, metapaths):
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
    statistic = [0] * 14
    real_duplicate_groups = set()

    normalized_feature_dict = {}
    similarity_dict = {}
    for potential_duplicate_group in potential_duplicate_groups:  
        if count % 30000 == 0:
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

        if id_name_dict[author_A][0] not in name_instance_dict or id_name_dict[author_B][0] not in name_instance_dict:
            print id_name_dict[author_A][0] + str(author_A)
            print id_name_dict[author_B][0] + str(author_B)
            continue

        if not name_comparable(name_instance_dict[id_name_dict[author_A][0]], name_instance_dict[id_name_dict[author_B][0]], name_statistics):
            continue

        similarity = compute_similarity_score(author_A, author_B, metapaths)
        if author_A == 135353:
            print id_name_dict[author_A][0] + ' vs ' + id_name_dict[author_B][0]
            print similarity
        if max(similarity) >= merge_threshold:
            if max(similarity) == merge_threshold:
                name_A = id_name_dict[author_A][0]
                name_B = id_name_dict[author_B][0]
                if name_A == '' or name_B == '':
                    continue
                # if SequenceMatcher(None, name_instance_dict[name_A].last_name, name_instance_dict[name_B].last_name).ratio() > 0.6:
                #     if name_A.last_name != name_B.last_name and \
                #             name_A.last_name[:-1] != name_B.last_name and \
                #             name_A.last_name != name_B.last_name[:-1] and \
                #             name_A.last_name[:-1] != name_B.last_name[:-1]:
                #         continue

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


def find_conflict_name(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics):
    conflict_ids = set()
    for (author_id, duplicate_group) in authors_duplicates_dict.iteritems():
        if not name_group_comparable(duplicate_group, name_instance_dict, id_name_dict, name_statistics):
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


def refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_dict, metapaths):
    for author_id in authors_duplicates_dict.iterkeys():
        if author_id in authors_duplicates_dict[author_id]:
            authors_duplicates_dict[author_id].remove(author_id)

    count = 0
    for author_id in authors_duplicates_dict.iterkeys():
        for duplicate_author_id in set(authors_duplicates_dict[author_id]):
            if not name_comparable(name_instance_dict[id_name_dict[author_id][0]], \
                    name_instance_dict[id_name_dict[duplicate_author_id][0]], name_statistics, False):
                authors_duplicates_dict[author_id].remove(duplicate_author_id)
                if author_id in authors_duplicates_dict[duplicate_author_id]:
                    authors_duplicates_dict[duplicate_author_id].remove(author_id)
                count += 1
    print "\tRemoving " + str(count) + " author_ids from name comparison."

    conflict_ids = find_conflict_name(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics)
    subset_similarity_dict = {}
    new_group_set = set()
    for author_id in conflict_ids:
        pool = authors_duplicates_dict[author_id]
        pool.add(author_id)
        for id in pool:
            new_group_set.add((id,))
        for candi1 in pool:
            for candi2 in pool:
                if candi1 != candi2:
                    if tuple(sorted((candi1, candi2))) not in similarity_dict:
                        similarity_dict[tuple(sorted((candi1, candi2)))] = max(compute_similarity_score(candi1, candi2, metapaths))
                    subset_similarity_dict[tuple(sorted((candi1, candi2)))] = similarity_dict[tuple(sorted((candi1, candi2)))]

    sorted_author_pairs = sorted(subset_similarity_dict.keys(), key=lambda candi: -subset_similarity_dict[candi])

    for author_pair in sorted_author_pairs:
        author1 = author_pair[0]
        author2 = author_pair[1]
        group1 = tuple()
        for group in new_group_set:
            if author1 in group:
                group1 = group
            if author2 in group:
                group2 = group
        if group1 == group2:
            continue
        new_group = set(group1 + group2)
        if not name_group_comparable(new_group, name_instance_dict, id_name_dict, name_statistics):
            continue
        else:
            new_group = tuple(sorted(new_group))
        if group1 in new_group_set:
            new_group_set.remove(group1)
        if group2 in new_group_set:
            new_group_set.remove(group2)
        new_group_set.add(new_group)

    for author_id in conflict_ids:
        new_group = authors_duplicates_dict[author_id]
        for group in new_group_set:
            if author_id in group:
                new_group = group
        for id in authors_duplicates_dict[author_id]:
            if id not in new_group and author_id in authors_duplicates_dict[id]:
                authors_duplicates_dict[id].remove(author_id)
        authors_duplicates_dict[author_id] = set(new_group)

    # count = 0
    # for author_id in conflict_ids:
    #     pool = authors_duplicates_dict[author_id]
    #     pool = sorted(pool, key=lambda candi: -similarity_dict[tuple(sorted((author_id, candi)))])
    #     group = [author_id]
    #     for candidate in pool:
    #         group.append(candidate)
    #         if not name_group_comparable(group, name_instance_dict, id_name_dict, name_statistics):
    #             group.pop()
    #     for id in authors_duplicates_dict[author_id]:
    #         if id not in group and author_id in authors_duplicates_dict[id]:
    #             authors_duplicates_dict[id].remove(author_id)
    #     authors_duplicates_dict[author_id] = set(group)
    #     count += 1
    #     if count % 100 == 0:
    #         print "\tFinish analysing " \
    #             + str(float(count)/len(conflict_ids)*100) \
    #             + "% (" + str(count) + "/" + str(len(conflict_ids)) \
    #             + ") conflict_ids."

    for author_id in authors_duplicates_dict.iterkeys():
        if author_id in authors_duplicates_dict[author_id]:
            authors_duplicates_dict[author_id].remove(author_id)

def pre_filter(authors_duplicates_dict, name_instance_dict, id_name_dict, similarity_dict, metapaths):
    count = 0
    for (author_id, group) in authors_duplicates_dict.iteritems():
        elements = id_name_dict[author_id][0].split()
        i = 0
        for element in elements:
            if len(element) > 1:
                i += 1
        if i >= 2:
            continue
        to_remove_set = set()
        for id in group:
            if id_name_dict[author_id][0] != id_name_dict[id][0]:
                if tuple(sorted((author_id, id))) not in similarity_dict:
                    similarity_dict[tuple(sorted((author_id, id)))] = max(compute_similarity_score(author_id, id, metapaths))
                if similarity_dict[tuple(sorted((author_id, id)))] <= 30:
                    to_remove_set.add(id)
        for id in to_remove_set:
            authors_duplicates_dict[author_id].remove(id)
            count += 1
            if author_id in authors_duplicates_dict[id]:
                authors_duplicates_dict[id].remove(author_id)
    print "\tFinish removing " + str(float(count)) \
                + " unconfident names."



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

    for author_id in authors_duplicates_dict.iterkeys():
        if id_name_dict[author_id][1] == '':
            authors_duplicates_dict[author_id] = set()
    
    