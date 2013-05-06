#-*- coding: UTF-8 -*-
import csv
import os
from SOAPpy import SOAPServer
from name import *
from soap_service import *
from custom_setting import *


def load_files():
    """Read in files from the folder "data".

    Returns:
        A tuple composed of two dictionaries.
        name_instance_dict:
            A dictionary with key: author's name string and value:
            name instance. Note that the author's name is clean after
            instantiation of the Name class.
        id_name_dict:
            A dictionary with key: author_id and value: author's name strings.
            Note that the value is a tuple of clean name and noisy name.
    """
    name_instance_dict = dict()
    id_name_dict = dict()
    name_statistics = dict()
    with open(author_file, 'rb') as csv_file:
        author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        #skip first line
        next(author_reader)
        for row in author_reader:
            author_id = int(row[0])
            author = Name(row[1])
            id_name_dict[author_id] = [author.name, row[1]]
            if author.name in name_instance_dict:
                name_instance_dict[author.name].add_author_id(int(row[0]))
            else:
                author.add_author_id(int(row[0]))
                name_instance_dict[author.name] = author
            if author.last_name in name_statistics:
                name_statistics[author.last_name] += 1
                name_statistics[author.first_name] += 1

    with open(paper_author_file, 'rb') as csv_file:
        paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        #skip first line
        next(paper_author_reader)
        for row in paper_author_reader:
            # paper_id = int(row[0])
            author_id = int(row[1])
            author = Name(row[2])
            if author_id in id_name_dict:  # and author.name != id_name_dict[author_id][0]:
                #name_instance_dict[id_name_dict[author_id][0]].add_alternative(author.name)
                id_name_dict[author_id].append(author.name)
                # print id_name_dict[author_id][0] + "->" + author.name
    return (name_instance_dict, id_name_dict, name_statistics)


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

    #####################################################
    # Further improvements:
    # For every name, find its similar author ids two hops away.
    # That is, find its similar authors' similar authors.
    # If the distance between them are small, add them into similar_author_ids.
    # e.g., Michael Jordan and M.I. Jordan are close but they're two hops away.
    # Moreover, Michael Jordan and Micheal Jordan are similar.


def sort_author_id(author_id, exact_author_ids, similar_author_ids):
    """Sort author_ids among exact_author_ids and similar_author_ids.

    Note: the author_id needs to be first removed.

    Parameters:
        exact_author_ids:
            Attribute: author_ids of the Name class.
        similar_author_ids:
            Attribute: similar_author_ids of the Name class.

    Return:
        A list of ranked author ids.
    """
    filetered_exact_author_ids = set(exact_author_ids)
    filetered_exact_author_ids.remove(author_id)
    return (list(filetered_exact_author_ids), list(similar_author_ids))

    #####################################################
    # Further improvements:
    # Consider the number of papers published under the assumption that
    # the more one author publishes papers, the more likely he/she
    # will be the duplicate.


def save_result(name_instance_dict, id_name_dict):
    """Generate the submission file.

    Note: the author_id needs to be first removed.

    Parameters:
        name_instance_dict:
            A dictionary with key: author's name string and value:
            name instance. Note that the author's name is clean after
            instantiation of the Name class.
        id_name_dict:
            A dictionary with key: author_id and value: author's name strings.
            Note that the value is a tuple of clean name and noisy name.
    """
    directory = os.path.dirname(duplicate_authors_file)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(duplicate_authors_file, 'wb') as result_file:
        result_file.write("AuthorId,DuplicateAuthorIds" + '\n')
        for author_id in sorted(id_name_dict.iterkeys()):
            result_file.write(str(author_id) + ',' + str(author_id))
            name_instance = name_instance_dict[id_name_dict[author_id][0]]
            sorted_ids = sort_author_id(author_id, name_instance.author_ids,
                                        name_instance.similar_author_ids)
            for id in sorted_ids[0]:
                result_file.write(' ' + str(id))
            for id in sorted_ids[1]:
                result_file.write(' ' + str(id))
            result_file.write('\n')
    # directory = os.path.dirname(duplicate_authors_file)
    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    # with open(duplicate_authors_file, 'wb') as result_file:
    #     result_file.write("AuthorId,DuplicateAuthorIds" + '\n')
    #     for author_id in sorted(id_name_dict.iterkeys()):
    #         name_instance = name_instance_dict[id_name_dict[author_id][0]]
    #         sorted_ids = sort_author_id(author_id, name_instance.author_ids,
    #                                     name_instance.similar_author_ids)
    #         if (len(sorted_ids[0]) + len(sorted_ids[1])) != 0:
    #             result_file.write(id_name_dict[author_id][1] + ' ' + str(author_id) + ',')
    #             for id in sorted_ids[0]:
    #                 result_file.write(' ' + id_name_dict[id][1] + ' ' + str(id))
    #             result_file.write('|')
    #             for id in sorted_ids[1]:
    #                 result_file.write(' ' + id_name_dict[id][1] + ' ' + str(id))
    #             result_file.write('\n')


if __name__ == '__main__':
    mode = raw_input("Type in number to choose running mode:\n" +
                     "(0: Generate Submission File, 1: Work as SOAP server)\n")
    if int(mode) == 0:
        (name_instance_dict, id_name_dict, name_statistics) = load_files()
        match_names(name_instance_dict)
        save_result(name_instance_dict, id_name_dict)
    elif int(mode) == 1:
        (name_instance_dict, id_name_dict, name_statistics) = load_files()
        match_names(name_instance_dict)

        server = SOAPServer((server_soap_address, server_port))
        soap_service = SOAPService(name_instance_dict, id_name_dict)
        server.registerObject(soap_service)
        print "SOAP service starts working."
        server.serve_forever()
