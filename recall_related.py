#-*- coding: UTF-8 -*-
from difflib import SequenceMatcher
from name import *


def add_similar_ids_under_name(name_instance_dict, id_name_dict):
    """Find similar id for each name in name_instance_dict.

    Parameters:
        name_instance_dict:
            A dictionary with key: author's name string and value:
            name instance. Note that the author's name is clean after
            instantiation of the Name class.
    """
    print "\tBuilding virtual names."
    virtual_name_set = set()
    for (author_name, name_instance) in name_instance_dict.iteritems():
        alternatives = name_instance.get_alternatives()
        for alternative in alternatives:
            if alternative not in name_instance_dict:
                virtual_name_set.add(alternative)

    for virtual_author_name in virtual_name_set:
        new_name_instance = Name(virtual_author_name)
        name_instance_dict[virtual_author_name] = new_name_instance

    print "\tAdding similar author ids into each name instance."
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            alternatives = name_instance.get_alternatives()
            for alternative in alternatives:
                # Add author_ids into the similar_author_ids
                # of the name's alternative.
                for id in name_instance.author_ids:
                    name_instance_dict[alternative].add_similar_author_id(id)
                # Add alternative's author_ids into the similar_author_ids
                # of the current name.
                for id in name_instance_dict[alternative].author_ids:
                    name_instance_dict[author_name].add_similar_author_id(id)
    
  
    length = len(name_instance_dict) - len(virtual_name_set)
    init_full_dict = {}
    full_init_dict = {}
    count = 0
    print "\tBuilding name initials mapping."
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            initials = ''
            # elements = author_name.split(' ')
            # for element in elements:
            #     if len(element) > 1:
            #         initials += element[0]
            if name_instance.first_name != '':
                initials += name_instance.first_name[0]
            if name_instance.middle_name != '':
                initials += name_instance.middle_name[0]
            if name_instance.last_name != '':
                initials += name_instance.last_name[0]
            init_full_dict.setdefault(initials, set()).add(author_name)
            full_init_dict[author_name] = initials

    print "\tStart arbitrary name comparison:"
    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            pool = init_full_dict[full_init_dict[author_name]]
            for candidate in pool:
                if author_name[:-1] == candidate:
                # if SequenceMatcher(None, author_name, candidate).ratio() >= 0.9:
                    name_instance_candidate = name_instance_dict[candidate]
                    for id in name_instance.author_ids:
                        name_instance_candidate.add_similar_author_id(id)
                    for id in name_instance_candidate.author_ids:
                        name_instance.add_similar_author_id(id)
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish matching " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names containing noisy last character with the whole database."
    print

    count = 0
    for (author_id, author_name_list) in id_name_dict.iteritems():
        if not all(ord(char) < 128 for char in author_name_list[1]) or author_name_list[1].find('?') >= 0:
            name_instance_dict[author_name_list[0]].bad_name_flag = True
            pool = init_full_dict[full_init_dict[author_name_list[0]]]
            for candidate in pool:
                if SequenceMatcher(None, author_name_list[0], candidate).ratio() >= 0.9 or SequenceMatcher(None, author_name_list[1], candidate).ratio() >= 0.9:
                    name_instance_candidate = name_instance_dict[candidate]
                    for id in name_instance_dict[author_name_list[0]].author_ids:
                        name_instance_candidate.add_similar_author_id(id)
                    for id in name_instance_candidate.author_ids:
                        name_instance_dict[author_name_list[0]].add_similar_author_id(id)                    
            count += 1
            if count % 1000 == 0:
                print "\t\tFinish matching " + str(count)\
                    + " names containing question mark or non askii characters with the whole database."
    print "\t\tIn total there exist " + str(count)\
        + " names containing question marks or non askii characters."
    print

    count = 0
    for (author_id, author_name_list) in id_name_dict.iteritems():
        pool = init_full_dict[full_init_dict[author_name_list[0]]]
        for candidate in pool:
            if SequenceMatcher(None, author_name_list[0], candidate).ratio() >= 0.94:
                name_instance_candidate = name_instance_dict[candidate]
                for id in name_instance_dict[author_name_list[0]].author_ids:
                    name_instance_candidate.add_similar_author_id(id)
                for id in name_instance_candidate.author_ids:
                    name_instance_dict[author_name_list[0]].add_similar_author_id(id)                    
        count += 1
        if count % 20000 == 0:
            print "\t\tFinish matching " + str(count)\
                + " names with the whole database."
    print


    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if name_instance.first_name in nickname_dict:
            for nickname in nickname_dict[name_instance.first_name]:
                s = ' '.join([nickname, name_instance.middle_name, name_instance.last_name]).strip()
                new_name = ' '.join(s.split())
                if new_name in name_instance_dict:
                    for id in name_instance_dict[new_name].author_ids:
                        name_instance.add_similar_author_id(id)
                    for id in name_instance.author_ids:
                        name_instance_dict[new_name].add_similar_author_id(id)
                    count += 1
                    if count % 2000 == 0:
                        print "\t\tFinish matching " + str(count)\
                            + " pairs of nicknames."

def create_potential_duplicate_groups(name_instance_dict):
    """Create potential duplicate groups for local clustering algorithm to analyse.

    Parameters:
        name_instance_dict:
            A dictionary with key: author's name string and value:
            name instance. Note that the author's name is clean after
            initialization of the Name class.

    Returns:
        A set containing lots of tuples describing the potential duplicate group.
    """
    # groups = set()
    # for (author_name, name_instance) in name_instance_dict.iteritems():
    #     groups.add(tuple(sorted(name_instance.author_ids.union(name_instance.similar_author_ids))))
    # return groups

    groups = set()
    for (author_name, name_instance) in name_instance_dict.iteritems():
        group = name_instance.author_ids.union(name_instance.similar_author_ids)
        for id1 in group:
            for id2 in group:
                if id1 < id2:
                    groups.add(tuple([id1, id2]))
    return groups
