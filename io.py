import csv
import os
import cPickle
from scipy.sparse import lil_matrix, spdiags
from name import *
from custom_setting import *


def load_files():
    """Read in files from the folder "data" if no serialization files exist in
       folder "to use".

    Returns:
        A tuple composed of several data structures.
        name_instance_dict:
            A dictionary with key: author's name string and value:
            name instance. Note that the author's name is clean after
            instantiation of the Name class.
        id_name_dict:
            A dictionary with key: author_id and value: list of author's name
            strings. Note that the value is a tuple of clean name and noisy
            name.
            clean name: name obtained from Name class.
            noisy name: name obtained from author.csv and paperauthor.csv.
        name_statistics:
            A dictionary with key: first name or last name and value: counts
            from author.csv.
        author_paper_matrix:
            A sparse matrix with row: author_id and column: paper id.
        coauthor_matrix:
            A sparse matrix with row: author_id and column: author_id.
            It is obtained from author_paper_matrix.
    """

    directory = os.path.dirname(serialization_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.isfile(serialization_dir + coauthor_matrix_file) and \
        os.path.isfile(serialization_dir + author_paper_matrix_file) and \
        os.path.isfile(serialization_dir + name_instance_file) and \
        os.path.isfile(serialization_dir + id_name_file) and \
            os.path.isfile(serialization_dir + name_statistics_file):
            #os.path.isfile(serialization_dir + covenue_matrix_file) and \
            #os.path.isfile(serialization_dir + author_venue_matrix_file) and \
        print "Serialization files exist."
        print "Read in the serialization files."
        coauthor_matrix = cPickle.load(
            open(serialization_dir + coauthor_matrix_file, "rb"))
        author_paper_matrix = cPickle.load(
            open(serialization_dir + author_paper_matrix_file, "rb"))
        # covenue_matrix = cPickle.load(open(
            # serialization_dir + covenue_matrix_file, "rb"))
        # author_venue_matrix = cPickle.load(
            # open(serialization_dir + author_venue_matrix_file, "rb"))
        name_instance_dict = cPickle.load(
            open(serialization_dir + name_instance_file, "rb"))
        id_name_dict = cPickle.load(
            open(serialization_dir + id_name_file, "rb"))
        name_statistics = cPickle.load(
            open(serialization_dir + name_statistics_file, "rb"))
    else:
        print "Serialization files do not exist."
        name_instance_dict = dict()
        id_name_dict = dict()
        name_statistics = dict()
        # The maximum id for author is 2293837 and for paper is 2259021
        author_paper_matrix = lil_matrix((2293837 + 1, 2259021 + 1))
        print "Read in the author.csv file."
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

        print "Read in the paperauthor.csv file."
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(
                csv_file, delimiter=',', quotechar='"')
            #skip first line
            next(paper_author_reader)
            count = 0
            for row in paper_author_reader:
                count += 1
                paper_id = int(row[0])
                author_id = int(row[1])
                author_paper_matrix[author_id, paper_id] = 1
                author = Name(row[2])
                if author_id in id_name_dict:
                    name_instance_dict[id_name_dict[author_id][0]].add_alternative(author.name)
                    id_name_dict[author_id].append(author.name)
                    # print id_name_dict[author_id][0] + "->" + author.name
        print "Computing the coauthor graph."
        coauthor_matrix = author_paper_matrix * author_paper_matrix.transpose()

        print "Remove diagonal elements in coauthor_matrix."
        coauthor_matrix = coauthor_matrix - spdiags(coauthor_matrix.diagonal(), 0, 2293837 + 1, 2293837 + 1, 'csr')

        print "Write into the serialization files."
        cPickle.dump(
            coauthor_matrix,
            open(serialization_dir + coauthor_matrix_file, "wb"), 2)
        cPickle.dump(
            author_paper_matrix,
            open(serialization_dir + author_paper_matrix_file, "wb"), 2)
        cPickle.dump(
            name_instance_dict,
            open(serialization_dir + name_instance_file, "wb"), 2)
        cPickle.dump(
            id_name_dict,
            open(serialization_dir + id_name_file, "wb"), 2)
        cPickle.dump(
            name_statistics,
            open(serialization_dir + name_statistics_file, "wb"), 2)
    return (name_instance_dict, id_name_dict, name_statistics,
            author_paper_matrix, coauthor_matrix)


def save_result(rank_authors_dict, name_instance_dict, id_name_dict):
    """Generate the submission file.

    Parameters:
        rank_authors_dict:
            A dictionary of ranked duplicate authors with key: author id
            and value: a sorted list of duplicate author ids
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
        length = len(rank_authors_dict)
        count = 0
        for author_id in sorted(rank_authors_dict.iterkeys()):
            count += 1
            if count % 1000 == 0:
                print "Finish writing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") lines."

            #result_file.write(str(len(rank_authors_dict[author_id])) + " " +
                # str(len(
                # name_instance_dict[id_name_dict[author_id][0]].author_ids))
                # + " ")
            #result_file.write(id_name_dict[author_id][1]
                # + ' ' + str(author_id) + ',')
            result_file.write(str(author_id) + ',' + str(author_id))
            for id in rank_authors_dict[author_id]:
                #result_file.write
                # (' ' + id_name_dict[id][1] + ' ' + str(id) + ',')
                result_file.write(' ' + str(id))
            #result_file.write("~~~~")
            #for id in name_instance_dict
            # [id_name_dict[author_id][0]].author_ids:
            #    result_file.write
                    # (' ' + id_name_dict[id][1] + ' ' + str(id) + ',')
            result_file.write('\n')
