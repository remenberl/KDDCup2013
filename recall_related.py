#-*- coding: UTF-8 -*-
from difflib import SequenceMatcher
from name import *


def add_similar_ids_under_name(name_instance_dict):
    """Find similar id for each name in name_instance_dict.

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
                # for id in name_instance.author_ids:
                #     name_instance_dict[alternative].add_similar_author_id(id)
                # Add alternative's author_ids into the similar_author_ids
                # of the current name.
                for id in name_instance_dict[alternative].author_ids:
                    name_instance_dict[author_name].add_similar_author_id(id)

    # length = len(name_instance_dict)
    # count = 0
    # for (author_name1, name_instance1) in name_instance_dict.iteritems():
    #     for (author_name2, name_instance2) in name_instance_dict.iteritems():
    #         if SequenceMatcher(None, author_name1, author_name2).real_quick_ratio() >= sequence_matcher_threshold:
    #             if SequenceMatcher(None, author_name1, author_name2).ratio() >= sequence_matcher_threshold:
    #                 for id in name_instance1.author_ids:
    #                     name_instance2.add_similar_author_id(id)
    #                 for id in name_instance2.author_ids:
    #                     name_instance1.add_similar_author_id(id)
    #     count += 1
    #     if count % 100 == 0:
    #         print "Finish matching " + str(float(count)/length*100)\
    #             + "% (" + str(count) + "/" + str(length) + ") names with the whole database."


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
    groups = set()
    for (author_name, name_instance) in name_instance_dict.iteritems():
        groups.add(tuple(sorted(name_instance.author_ids.union(name_instance.similar_author_ids))))
    return groups
