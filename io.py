#-*- coding: UTF-8 -*-
import csv
import os
import cPickle
from scipy.sparse import lil_matrix, dok_matrix, spdiags
from difflib import SequenceMatcher
from name import *
from custom_setting import *


def load_author_files():
    directory = os.path.dirname(serialization_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.isfile(serialization_dir + name_instance_file) and \
        os.path.isfile(serialization_dir + id_name_file) and \
            os.path.isfile(serialization_dir + name_statistics_file):
        print "\tSerialization files related to authors exist."
        print "\tReading in the serialization files."
        name_instance_dict = cPickle.load(
            open(serialization_dir + name_instance_file, "rb"))
        id_name_dict = cPickle.load(
            open(serialization_dir + id_name_file, "rb"))
        name_statistics = cPickle.load(
            open(serialization_dir + name_statistics_file, "rb"))
    else:
        print "\tSerialization files related to authors do not exist."
        name_instance_dict = dict()
        id_name_dict = dict()
        name_statistics = dict()
        print "\tReading in the author.csv file."
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

                if author.last_name not in name_statistics:
                    name_statistics[author.last_name] = 0
                else:
                    name_statistics[author.last_name] += 1

                if author.first_name not in name_statistics:
                    name_statistics[author.first_name] = 0
                else:
                    name_statistics[author.first_name] += 1

        print "\tWriting into serialization files related to authors."
        cPickle.dump(
            name_instance_dict,
            open(serialization_dir + name_instance_file, "wb"), 2)
        cPickle.dump(
            id_name_dict,
            open(serialization_dir + id_name_file, "wb"), 2)
        cPickle.dump(
            name_statistics,
            open(serialization_dir + name_statistics_file, "wb"), 2)

    return (name_instance_dict, id_name_dict, name_statistics)


def load_coauthor_files(name_instance_dict, id_name_dict, name_statistics):
    if os.path.isfile(serialization_dir + coauthor_matrix_file) and \
            os.path.isfile(serialization_dir + author_paper_matrix_file):
        print "\tSerialization files related to coauthors exist."
        print "\tReading in the serialization files."
        coauthor_matrix = cPickle.load(
            open(serialization_dir + coauthor_matrix_file, "rb"))
        author_paper_matrix = cPickle.load(
            open(serialization_dir + author_paper_matrix_file, "rb"))
    else:
        print "\tSerialization files related to coauthors do not exist."
        # The maximum id for author is 2293837 and for paper is 2259021
        full_author_paper_matrix = lil_matrix((max_author + 1, max_paper + 1))
        author_paper_matrix = lil_matrix((max_author + 1, max_paper + 1))
        print "\tReading in the paperauthor.csv file."
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(
                csv_file, delimiter=',', quotechar='"')
            # skip first line
            next(paper_author_reader)
            count = 0
            for row in paper_author_reader:
                count += 1
                if count % 100000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
                paper_id = int(row[0])
                author_id = int(row[1])
                full_author_paper_matrix[author_id, paper_id] = 1
                author = Name(row[2], True)
                if author.last_name not in name_statistics:
                    name_statistics[author.last_name] = 0
                else:
                    name_statistics[author.last_name] += 1

                if author.first_name not in name_statistics:
                    name_statistics[author.first_name] = 0
                else:
                    name_statistics[author.first_name] += 1

                if author_id in id_name_dict:
                    author_paper_matrix[author_id, paper_id] = 1
                    # add names appeared in paperauthor.csv
                    if author.last_name == name_instance_dict[id_name_dict[author_id][0]].last_name:
                        name_instance_dict[id_name_dict[author_id][0]].add_alternative(author.name)
                        id_name_dict[author_id].append(author.name)
                    elif SequenceMatcher(None, author.name, id_name_dict[author_id][0]).real_quick_ratio() >= sequence_matcher_threshold:
                        if SequenceMatcher(None, author.name, id_name_dict[author_id][0]).ratio() >= sequence_matcher_threshold:
                            name_instance_dict[id_name_dict[author_id][0]].add_alternative(author.name)
                            id_name_dict[author_id].append(author.name)
        print "\tComputing the coauthor graph."
        coauthor_matrix = author_paper_matrix * full_author_paper_matrix.transpose()

        print "\tRemoving diagonal elements in coauthor_matrix."
        coauthor_matrix = coauthor_matrix - spdiags(coauthor_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')

        print "\tWriting into serialization files related to coauthors."
        cPickle.dump(
            coauthor_matrix,
            open(serialization_dir + coauthor_matrix_file, "wb"), 2)
        cPickle.dump(
            author_paper_matrix,
            open(serialization_dir + author_paper_matrix_file, "wb"), 2)
    
    return (author_paper_matrix, coauthor_matrix)


def load_covenue_files(id_name_dict, author_paper_matrix):
    if os.path.isfile(serialization_dir + covenue_matrix_file):
        print "\tSerialization files related to author_venue exist."
        print "\tReading in the serialization files."
        covenue_matrix = cPickle.load(open(
            serialization_dir + covenue_matrix_file, "rb"))
    else:
        print "\tSerialization files related to author_venue do not exist."
        # The maximum id for journal is 5222 and for conference is 22228
        # full_author_venue_matrix = lil_matrix((max_author + 1, max_conference + max_journal + 1))
        paper_venue_matrix = lil_matrix((max_paper + 1, max_conference + max_journal + 1))
        print "\tReading in the sanitizedPaper.csv file."
        with open(paper_file, 'rb') as csv_file:
            paper_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # skip first line
            next(paper_reader)
            for row in paper_reader:
                paper_id = int(row[0])
                conference = int(row[3])
                journal = int(row[4])
                # id_name_dict[author_id] = [author.name, row[1]]
                if conference > 0:
                    paper_venue_matrix[paper_id, conference + max_journal] = 1
                elif journal > 0:
                    paper_venue_matrix[paper_id, journal] = 1

        print "\tComputing the author_venue matrix."
        author_venue_matrix = author_paper_matrix * paper_venue_matrix
        # full_author_venue_matrix = full_author_paper_matrix * paper_venue_matrix
        # print len(row), len(col)

        print "\tComputing the covenue matrix."
        covenue_matrix = author_venue_matrix * author_venue_matrix.transpose()
       
        # del author_venue_matrix, full_author_venue_matrix

        print "\tRemoving diagonal elements in covenue_matrix."
        covenue_matrix = covenue_matrix - spdiags(covenue_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')

        print "\tWriting into serialization files related to author_venue."
        cPickle.dump(
            covenue_matrix,
            open(serialization_dir + covenue_matrix_file, "wb"), 2)

    return covenue_matrix


def load_author_word_files(id_name_dict, author_paper_matrix):
    if os.path.isfile(serialization_dir + author_word_matrix_file):
        print "\tSerialization files related to author_word exist."
        print "\tReading in the serialization files."
        author_word_matrix = cPickle.load(open(
            serialization_dir + author_word_matrix_file, "rb"))
    else:
        print "\tSerialization files related to author_word do not exist."

        # stopwords = set()
        # print "\tReading in stopword file."
        # with open(stopword_file, 'rb') as csv_file:
        #     stopword_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        #     # skip first line
        #     next(stopword_reader)
        #     for row in stopword_reader:
        #         if row:
        #             stopwords.add(row[0].strip())

        print "\tReading in the sanitizedPaper.csv file and roughly filter words."
        word_statistic_dict = {}
        with open(paper_file, 'rb') as csv_file:
            paper_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # skip first line
            next(paper_reader)
            index = 0
            for row in paper_reader:
                paper_id = int(row[0])
                title = row[1]
                words = title.split(' ')
                for word in words:
                    word = word.strip().lower()
                    if word != "":
                        word_statistic_dict.setdefault(word, 0)
                        word_statistic_dict[word] += 1
        stopwords = set()
        max_word = 0
        for (word, count) in word_statistic_dict.iteritems():
            if count <= 1 or count > 1000:
                stopwords.add(word)
            else:
                max_word += 1
        print "\tThere are in totoal " + str(max_word) + " words."
        max_word -= 1
        print "\tComputing the paper_word matrix."
        paper_word_matrix = lil_matrix((max_paper + 1, max_word + 1))

        word_id_dict = {}
        id_word_dict = {}
        with open(paper_file, 'rb') as csv_file:
            paper_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # skip first line
            next(paper_reader)
            index = 0
            for row in paper_reader:
                paper_id = int(row[0])
                title = row[1]
                words = title.split(' ')
                for word in words:
                    word = word.strip().lower()
                    if word not in stopwords and word != "":
                        if word not in word_id_dict:
                            word_id_dict[word] = index
                            id_word_dict[index] = word
                            paper_word_matrix[paper_id, index] = 1
                            index += 1
                        else:
                            paper_word_matrix[paper_id, word_id_dict[word]] = 1

        print "\tComputing the author_word matrix."
        author_word_matrix = author_paper_matrix * paper_word_matrix

        author_word_count = author_word_matrix.sum(0)
        count = 0
        for word_index in xrange(max_word + 1):
            if author_word_count[0, word_index] <= 1 or author_word_count[0, word_index] > word_title_count_threshold:
                stopwords.add(id_word_dict[word_index])
                count += 1

        print "\tRemoving " + str(count) + " words." 
        print "\tRecomputing the paper_word matrix."
        paper_word_matrix = lil_matrix((max_paper + 1, max_word - count + 1))

        word_id_dict = {}
        with open(paper_file, 'rb') as csv_file:
            paper_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # skip first line
            next(paper_reader)
            index = 0
            for row in paper_reader:
                paper_id = int(row[0])
                title = row[1]
                words = title.split(' ')
                for word in words:
                    word = word.strip().lower()
                    if word not in stopwords and word != "":
                        if word not in word_id_dict:
                            word_id_dict[word] = index
                            paper_word_matrix[paper_id, index] = 1
                            index += 1
                        else:
                            paper_word_matrix[paper_id, word_id_dict[word]] = 1

        print "\tRecomputing the author_word matrix."
        author_word_matrix = author_paper_matrix * paper_word_matrix

        print "\tWriting into serialization files related to author_word."
        cPickle.dump(
            author_word_matrix,
            open(serialization_dir + author_word_matrix_file, "wb"), 2)
    return author_word_matrix


def load_files():
    """Read in files from the folder "data" if no serialization files exist in
       folder serialization_dir.

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

        --- added by Chi ---
        #paper_venue_dict:
        #    A dictionary with key: paper_id and value: venue id
        #    conference id and journal id are merged
        author_venue_matrix:
            A sparse matrix with row: author_id and column: venue_id
            It is obtained by joining author_paper_matrix with paper_venue_dict
        covenue_matrix:
            A sparse matrix with row: author_id and column: author_id.
            It is obtained by joining author_venue_matrix with itself
    """
    (name_instance_dict, id_name_dict, name_statistics) = load_author_files()
    print
    (author_paper_matrix, coauthor_matrix) = load_coauthor_files(name_instance_dict, id_name_dict, name_statistics)
    print
    covenue_matrix = load_covenue_files(id_name_dict, author_paper_matrix)
    print
    author_word_matrix = load_author_word_files(id_name_dict, author_paper_matrix)

    return (name_instance_dict, id_name_dict, name_statistics,
            coauthor_matrix,
            covenue_matrix,
            author_word_matrix)


def save_result(authors_duplicates_dict, name_instance_dict, id_name_dict):
    """Generate the submission file and fullname file for analysis.

    Parameters:
        authors_duplicates_dict:
            A dictionary of duplicate authors with key: author id
            and value: a set of duplicate author ids
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
        for author_id in sorted(authors_duplicates_dict.iterkeys()):
            result_file.write(str(author_id) + ',' + str(author_id))
            id_list = sorted(authors_duplicates_dict[author_id])
            for id in id_list:
                result_file.write(' ' + str(id))
            result_file.write('\n')

    with open(duplicate_authors_full_name_file, 'wb') as result_file:
        for author_id in sorted(authors_duplicates_dict.iterkeys()):
            result_file.write(id_name_dict[author_id][1]
                              + ' ' + str(author_id))
            id_list = sorted(authors_duplicates_dict[author_id])
            for id in id_list:
                result_file.write(', ' + id_name_dict[id][1] + ' ' + str(id))
            result_file.write('\n')
