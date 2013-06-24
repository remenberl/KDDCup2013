#-*- coding: UTF-8 -*-
from difflib import SequenceMatcher
from name import *

def add_similar_ids_under_name(name_instance_dict, id_name_dict, author_paper_stat):
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
    

    reduced_name_pool = {}
    length = len(name_instance_dict) - len(virtual_name_set)
    print "\tBuilding reduced_name dict."
    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish computing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names' hash value."
            elements = sorted(author_name.split())
            reduced_name = ''.join(elements)
            reduced_name_pool.setdefault(reduced_name, set()).add(author_name)

    print "\tAdding similar ids for the same reduced_names."
    count = 0
    for (author_name1, name_instance1) in name_instance_dict.iteritems():
        if author_name1 not in virtual_name_set:
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish comparing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names."
            elements = sorted(author_name1.split())
            reduced_name = ''.join(elements)
            pool = reduced_name_pool[reduced_name]
            for author_name2 in pool:
                if author_name1 < author_name2: 
                    name_instance2 = name_instance_dict[author_name2]
                    for id in name_instance1.author_ids:
                        name_instance2.add_similar_author_id(id)
                    for id in name_instance2.author_ids:
                        name_instance1.add_similar_author_id(id)             

    sorted_name_pool = {}
    length = len(name_instance_dict) - len(virtual_name_set)
    print "\tBuilding sorted name dict."
    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish computing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names' hash value."
            elements = author_name.split()
            sorted_name = ''.join(elements)
            sorted_name_pool.setdefault(sorted_name, set()).add(author_name)

    print "\tAdding similar ids for the same sorted_names."
    count = 0
    for (author_name1, name_instance1) in name_instance_dict.iteritems():
        if author_name1 not in virtual_name_set:
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish comparing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names."
            elements = author_name1.split()
            sorted_name = ''.join(elements)
            pool = sorted_name_pool[sorted_name]
            for author_name2 in pool:
                if author_name1 < author_name2: 
                    name_instance2 = name_instance_dict[author_name2]
                    for id in name_instance1.author_ids:
                        name_instance2.add_similar_author_id(id)
                    for id in name_instance2.author_ids:
                        name_instance1.add_similar_author_id(id)  


    name_unit_pool = {}
    length = len(name_instance_dict) - len(virtual_name_set)
    print "\tBuilding name unit dict."
    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            # if len(author_name) < 10:
            #     continue
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish computing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names' hash value."
            elements = name_instance.name.split()
            for element in elements:
                name_unit_pool.setdefault(element, set()).add(author_name)
    
    print "\tAdding similar ids for the same name units."
    count = 0
    for (author_name1, name_instance1) in name_instance_dict.iteritems():
        if author_name1 not in virtual_name_set:
            if len(author_name1) < 10:
                continue
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish comparing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names."
            elements = name_instance1.name.split()
            for element in elements:
                if len(element) < 7:
                    continue
                pool = name_unit_pool[element]
                for author_name2 in pool:
                    if author_name1 < author_name2: 
                        if author_name1.find(author_name2) >=0 or author_name2.find(author_name1) >= 0:
                            if abs(len(author_name1) - len(author_name2)) <= 3 and len(author_name1) >= 8 and len(author_name2) >= 8 or\
                                    len(author_name1) > 15 and len(author_name2) > 15:
                                name_instance2 = name_instance_dict[author_name2]
                                for id in name_instance1.author_ids:
                                    name_instance2.add_similar_author_id(id)
                                for id in name_instance2.author_ids:
                                    name_instance1.add_similar_author_id(id)
                        # print author_name2 + ' ' + author_name1

    # hash_dict = {}
    # hash_pool = {}
    # length = len(name_instance_dict) - len(virtual_name_set)
    # print "\tBuilding hashes."
    # count = 0
    # for (author_name, name_instance) in name_instance_dict.iteritems():
    #     if author_name not in virtual_name_set:
    #         count += 1
    #         if count % 30000 == 0:
    #             print "\t\tFinish computing " + str(float(count)/length*100)\
    #                 + "% (" + str(count) + "/" + str(length) + ") names' hash value."
    #         tokens = list()
    #         reduced_name = author_name.replace(' ', '')
    #         for i in xrange(len(reduced_name) - 2):
    #             tokens.append(reduced_name[i:i+3])
    #         hash_dict[author_name] = Simhash(tokens, 20)
    #         hash_pool.setdefault(hash_dict[author_name].hash, set()).add(author_name)

    # print "\tComparing hashes."
    # count = 0
    # for (author_name1, name_instance1) in name_instance_dict.iteritems():
    #     if author_name1 not in virtual_name_set:
    #         count += 1
    #         if count % 30000 == 0:
    #             print "\t\tFinish comparing " + str(float(count)/length*100)\
    #                 + "% (" + str(count) + "/" + str(length) + ") names."
    #         pool = hash_pool[hash_dict[author_name1].hash]
    #         for author_name2 in pool:
    #             if author_name1 <= author_name2: 
    #                 name_instance2 = name_instance_dict[author_name2]
    #                 for id in name_instance1.author_ids:
    #                     name_instance2.add_similar_author_id(id)
    #                 for id in name_instance2.author_ids:
    #                     name_instance1.add_similar_author_id(id)             


    length = len(name_instance_dict) - len(virtual_name_set)
    init_full_dict = {}
    full_init_dict = {}
    initlen_full_dict = {}
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
            initlen_full_dict.setdefault((initials, len(author_name)), set()).add(author_name)

    print "\tStart noisy last name comparison:"
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
    
    print "\tStart question marks or non askii name comparison:"
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
            if count % 300 == 0:
                print "\t\tFinish matching " + str(count)\
                    + " names containing question mark or non askii characters with the whole database."
    print "\t\tIn total there exist " + str(count) + " names containing question marks or non askii characters."


    # print "\tStart arbitrary name comparison with same units:"
    # count = 0
    # for (author_name, name_instance) in name_instance_dict.iteritems():
    #     if author_name not in virtual_name_set:
    #         elements = author_name.split()
    #         for element in elements:
    #             if len(element) <= 5:
    #                 continue
    #             if element in name_unit_pool:
    #                 pool = name_unit_pool[element]
    #                 for candidate in pool:
    #                     if SequenceMatcher(None, author_name, candidate).ratio() >= 0.94:
    #                         name_instance_candidate = name_instance_dict[candidate]
    #                         for id in name_instance_dict[author_name].author_ids:
    #                             name_instance_candidate.add_similar_author_id(id)
    #                         for id in name_instance_candidate.author_ids:
    #                             name_instance_dict[author_name].add_similar_author_id(id)
    #         count += 1
    #         if count % 30000 == 0:
    #             print "\t\tFinish matching " + str(float(count)/length*100)\
    #                 + "% (" + str(count) + "/" + str(length) + ") names with the whole database."
    # print

    # print "\tStart arbitrary name comparison with same initials:"
    # count = 0
    # for (author_name, name_instance) in name_instance_dict.iteritems():
    #     if author_name not in virtual_name_set:
    #         name_length = len(author_name)
    #         for area in range(-3, 4):
    #             if name_length + area > 0 and (full_init_dict[author_name], name_length + area) in initlen_full_dict:
    #                 pool = initlen_full_dict[(full_init_dict[author_name], name_length + area)]
    #                 for candidate in pool:
    #                     if SequenceMatcher(None, author_name, candidate).ratio() >= 0.94:
    #                         name_instance_candidate = name_instance_dict[candidate]
    #                         for id in name_instance_dict[author_name].author_ids:
    #                             name_instance_candidate.add_similar_author_id(id)
    #                         for id in name_instance_candidate.author_ids:
    #                             name_instance_dict[author_name].add_similar_author_id(id)                    
    #         count += 1
    #         if count % 30000 == 0:
    #             print "\t\tFinish matching " + str(float(count)/length*100)\
    #                 + "% (" + str(count) + "/" + str(length) + ") names with the whole database."
    # print

    print "\tStart nicknames comparison:"
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

def create_potential_duplicate_groups(name_instance_dict, author_paper_stat):
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
            if id1 in author_paper_stat:
                for id2 in group:
                    if id2 in author_paper_stat:
                        if id1 < id2:
                            groups.add(tuple([id1, id2]))
    return groups
