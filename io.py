#-*- coding: UTF-8 -*-
import csv
import os
import cPickle
import re
from scipy.sparse import lil_matrix, dok_matrix, spdiags
from difflib import SequenceMatcher
from name import *
from custom_setting import *


class Metapaths(object):
    """docstring for ClassName"""
    def __init__(self, AP, AV, AW, AK, APA, AVA):
        #AP: author-paper
        #AV: author-venue
        #APA: author-paper-venue
        #AVA: author-venue-author
        #AW: author-word
        #AK: author-keyword
        self.AP = AP
        self.AV = AV
        self.AW = AW
        self.AK = AK
        self.APA = APA
        self.AVA = AVA
         

def load_name_statistic():
    directory = os.path.dirname(serialization_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.isfile(serialization_dir + name_statistics_file):
        print "\tSerialization files related to name_statistics exist."
        print "\tReading in the serialization files.\n"
        name_statistics = cPickle.load(
            open(serialization_dir + name_statistics_file, "rb"))
    else:
        print "\tSerialization files related to name_statistics do not exist."
        name_statistics = dict()
        print "\tReading in the author.csv file."
        with open(author_file, 'rb') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            #skip first line
            next(author_reader)
            count = 0
            for row in author_reader:
                count += 1
                if count % 20000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
                author_name = row[1].lower().strip()
                elements = author_name.split(' ')
                for element in elements:
                    if element != '':
                        name_statistics[element] = name_statistics.setdefault(element, 0) + 1

        print "\tWriting into serialization files related to name_statistics.\n"
        cPickle.dump(
            name_statistics,
            open(serialization_dir + name_statistics_file, "wb"), 2)
    return name_statistics
  
 
def load_author_files(name_statistics):
    directory = os.path.dirname(serialization_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.isfile(serialization_dir + name_instance_file) and \
            os.path.isfile(serialization_dir + id_name_file):
        print "\tSerialization files related to authors exist."
        print "\tReading in the serialization files.\n"
        name_instance_dict = cPickle.load(
            open(serialization_dir + name_instance_file, "rb"))
        id_name_dict = cPickle.load(
            open(serialization_dir + id_name_file, "rb"))
    else:
        print "\tSerialization files related to authors do not exist."
        name_instance_dict = dict()
        id_name_dict = dict()
        print "\tReading in the author.csv file."
        with open(author_file, 'rb') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            #skip first line
            next(author_reader)
            count = 0
            for row in author_reader:
                count += 1
                if count % 20000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
                author_id = int(row[0])
                author_name = row[1]

                elements = author_name.split(" ")
                if author_name.upper()[:-1] == author_name[:-1]:
                    new_elements = elements
                else:
                    new_elements = list()
                    for element in elements:
                        if element.lower() in name_statistics:
                            if len(element) < 3 and name_statistics[element.lower()] <= 1:
                                new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                            elif len(element) >= 3 and name_statistics[element.lower()] <= 1:
                                if element.lower()[:-1] not in name_statistics or name_statistics[element.lower()[:-1]] <= 1:
                                    new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                                else:
                                    new_elements.append(element)
                            else:
                                new_elements.append(element)
                        else:
                            new_elements.append(element)
                author = Name(' '.join(new_elements))
                id_name_dict[author_id] = [author.name, row[1]]
                if author.name in name_instance_dict:
                    name_instance_dict[author.name].add_author_id(int(row[0]))
                else:
                    author.add_author_id(int(row[0]))
                    name_instance_dict[author.name] = author

        print "\tWriting into serialization files related to authors.\n"
        cPickle.dump(
            name_instance_dict,
            open(serialization_dir + name_instance_file, "wb"), 2)
        cPickle.dump(
            id_name_dict,
            open(serialization_dir + id_name_file, "wb"), 2)
 
    return (name_instance_dict, id_name_dict)


def load_coauthor_files(name_instance_dict, id_name_dict):
    if os.path.isfile(serialization_dir + coauthor_matrix_file) and \
            os.path.isfile(serialization_dir + author_paper_matrix_file) and \
            os.path.isfile(serialization_dir + 'all_' + author_paper_matrix_file) and \
            os.path.isfile(serialization_dir + 'complete_' + name_instance_file) and \
            os.path.isfile(serialization_dir + 'complete_' + id_name_file) and \
            os.path.isfile(serialization_dir + 'complete_' + author_paper_stat_file) :
        print "\tSerialization files related to coauthors exist."
        print "\tReading in the serialization files.\n"
        coauthor_matrix = cPickle.load(
            open(serialization_dir + coauthor_matrix_file, "rb"))
        author_paper_matrix = cPickle.load(
            open(serialization_dir + author_paper_matrix_file, "rb"))
        all_author_paper_matrix = cPickle.load(
            open(serialization_dir + 'all_' + author_paper_matrix_file, "rb"))
        name_instance_dict = cPickle.load(
            open(serialization_dir + 'complete_' + name_instance_file, "rb"))
        id_name_dict = cPickle.load(
            open(serialization_dir + 'complete_' + id_name_file, "rb"))
        author_paper_stat = cPickle.load(
            open(serialization_dir + 'complete_' + author_paper_stat_file, "rb"))
    else:
        print "\tSerialization files related to coauthors do not exist."
        # The maximum id for author is 2293837 and for paper is 2259021
        all_author_paper_matrix = lil_matrix((max_author + 1, max_paper + 1))
        author_paper_matrix = lil_matrix((max_author + 1, max_paper + 1))
        author_paper_stat = dict()
        print "\tReading in the paperauthor.csv file."
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(
                csv_file, delimiter=',', quotechar='"')
            # skip first line
            next(paper_author_reader)
            count = 0
            for row in paper_author_reader:
                count += 1
                if count % 500000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
                paper_id = int(row[0])
                author_id = int(row[1])
                if author_id in author_paper_stat:
                    author_paper_stat[author_id] += 1
                else:
                    author_paper_stat[author_id] = 1
                all_author_paper_matrix[author_id, paper_id] = 1
                author = Name(row[2], True)
                if author_id in id_name_dict:
                    author_paper_matrix[author_id, paper_id] = 1
                    # add names appeared in paperauthor.csv
                    if author.last_name == name_instance_dict[id_name_dict[author_id][0]].last_name:
                        name_instance_dict[id_name_dict[author_id][0]].add_alternative(author.name)
                        id_name_dict[author_id].append(author.name)
                    elif SequenceMatcher(None, author.name, id_name_dict[author_id][0]).ratio() >= 0.6:
                        name_instance_dict[id_name_dict[author_id][0]].add_alternative(author.name)
                        id_name_dict[author_id].append(author.name)
        print "\tComputing the coauthor graph."
        coauthor_matrix = author_paper_matrix * all_author_paper_matrix.transpose()

        print "\tRemoving diagonal elements in coauthor_matrix."
        coauthor_matrix = coauthor_matrix - spdiags(coauthor_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')

        print "\tWriting into serialization files related to coauthors.\n"
        cPickle.dump(
            coauthor_matrix,
            open(serialization_dir + coauthor_matrix_file, "wb"), 2)
        cPickle.dump(
            author_paper_matrix,
            open(serialization_dir + author_paper_matrix_file, "wb"), 2)
        cPickle.dump(
            author_paper_matrix,
            open(serialization_dir + "all_" + author_paper_matrix_file, "wb"), 2)
        cPickle.dump(
            name_instance_dict,
            open(serialization_dir + 'complete_' + name_instance_file, "wb"), 2)
        cPickle.dump(
            id_name_dict,
            open(serialization_dir + 'complete_' + id_name_file, "wb"), 2)
        cPickle.dump(
            author_paper_stat,
            open(serialization_dir + 'complete_' + author_paper_stat_file, "wb"), 2)
    
    return (author_paper_matrix, all_author_paper_matrix, coauthor_matrix, name_instance_dict, id_name_dict, author_paper_stat)


def load_covenue_files(id_name_dict, author_paper_matrix, all_author_paper_matrix):
    if os.path.isfile(serialization_dir + author_venue_matrix_file) and \
            os.path.isfile(serialization_dir + 'all_' + author_venue_matrix_file):
        print "\tSerialization files related to author_venue exist."
        print "\tReading in the serialization files."
        # covenue_matrix = cPickle.load(open(
        #     serialization_dir + covenue_matrix_file, "rb"))
        author_venue_matrix = cPickle.load(open(
            serialization_dir + author_venue_matrix_file, "rb"))
        all_author_venue_matrix = cPickle.load(open(
            serialization_dir + 'all_' + author_venue_matrix_file, "rb"))
    else:
        print "\tSerialization files related to author_venue do not exist."
        # The maximum id for journal is 5222 and for conference is 22228
        all_author_venue_matrix = lil_matrix((max_author + 1, max_conference + max_journal + 1))
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
        all_author_venue_matrix = all_author_paper_matrix * paper_venue_matrix
        # del author_venue_matrix, all_author_venue_matrix

        print "\tWriting into serialization files related to author_venue.\n"
        cPickle.dump(
            author_venue_matrix,
            open(serialization_dir + author_venue_matrix_file, "wb"), 2)
        cPickle.dump(
            all_author_venue_matrix,
            open(serialization_dir + 'all_' + author_venue_matrix_file, "wb"), 2)

    print "\tComputing the covenue matrix."
    covenue_matrix = author_venue_matrix * all_author_venue_matrix.transpose()
    print "\tRemoving diagonal elements in covenue_matrix.\n"
    covenue_matrix = covenue_matrix - spdiags(covenue_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')

    return (covenue_matrix, author_venue_matrix)


def load_author_word_files(id_name_dict, author_paper_matrix):
    if os.path.isfile(serialization_dir + author_word_matrix_file):
        print "\tSerialization files related to author_word exist."
        print "\tReading in the serialization files.\n"
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
            if count <= 1 or count > 500000:
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

        print "\tWriting into serialization files related to author_word.\n"
        cPickle.dump(
            author_word_matrix,
            open(serialization_dir + author_word_matrix_file, "wb"), 2)
    return author_word_matrix


def load_author_keyword_files(author_paper_matrix):
    if os.path.isfile(serialization_dir + author_key_word_matrix_file):
        print "\tSerialization files related to author_keyword exist."
        print "\tReading in the serialization files."
        author_key_word_matrix = cPickle.load(open(
            serialization_dir + author_key_word_matrix_file, "rb"))
    else:
        print "\tSerialization files related to author_keyword do not exist."
        nAuthor = author_paper_matrix.shape[0]-1
        nPaper = author_paper_matrix.shape[1]-1
        count = 0 #to count the # of unique key words
        dict_paper_keyWord = dict() #key: paperID. value: list of key words
        dict_keyWord = dict() #maps a keyWord to the corresponding column in paper_keyword_matrix

        print "\tReading in the Paper.csv file."
        with open("./data/Paper.csv", 'rb') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            count = 0 
            for row in csv_reader:
                paper_id = int(row[0])
                keyWords = row[5]
                #a valid key word list of a paper can't have more than 20 words
                if len(keyWords) > 0 and len(keyWords) < 50: 
                    keyWords = keyWords.lower()
                    keyWords = keyWords.split(' ') #parse each keyword by ' '
                    nW = len(keyWords)
                    if nW > 0:
                        for i in range(0,nW):
                            tmpWord = keyWords[i] 
                            tmpWord = tmpWord.replace(',','').replace(' ','').replace(':','').\
                                        replace('.','').replace(';','').replace('-','').replace('|','') 
                            #if re.match("^[a-zA-Z0-9]+$", tmpWord): #valid keyword should only contai 0-9 or a-zA-Z
                            if re.match("^[a-zA-Z]+$", tmpWord): #valid keyword should only contain a-zA-Z
                                #valid keyword should have [4,15] characters, and can't be the word "keyword" or "key" or "word"
                                condi = len(tmpWord) <= 15 and len(tmpWord) >=4 and 'key' not in tmpWord and 'word' not in tmpWord 
                                if condi: #if all conditions met for tmpWord to be a valid key word
                                    if tmpWord not in dict_keyWord:
                                        dict_keyWord[tmpWord] = count #
                                        count += 1 #whenever there is a unique new word, count++
                                    if paper_id not in dict_paper_keyWord:
                                        dict_paper_keyWord[paper_id] = [tmpWord]
                                    else:
                                        dict_paper_keyWord[paper_id].append(tmpWord)         
                                        
        nUniqueKeyWord = count 
        print "\tSummary:", nUniqueKeyWord, "unique keywords identified, contained in", \
                len(dict_paper_keyWord), "papers"
                 
        #computing paper_keyword_matrix
        print "\tComputing the co-key-word graph."
        paper_keyword_matrix = lil_matrix((nPaper+1, nUniqueKeyWord ))
        for paper_id in dict_paper_keyWord.keys():
            key_words = dict_paper_keyWord[paper_id]
            for word in key_words: 
                paper_keyword_matrix[paper_id, dict_keyWord[word]] += 1
        
        author_key_word_matrix = author_paper_matrix * paper_keyword_matrix 
        
        # print "\tComputing the co-key-word graph."
        # co_keyword_matrix = author_key_word_matrix * author_key_word_matrix.transpose()
        # co_keyword_matrix = co_keyword_matrix - spdiags(co_keyword_matrix.diagonal(), 0, nAuthor+1, nAuthor+1, 'csr')

        #store unique key-words into txt file for manual check
        with open("./data/list_paper_key_words.txt", 'wb') as keyWord_file:
            keyWord_file.write('Unique Key Words: n = ' + str(len(dict_keyWord)) + '\n')
            for key_id in dict_keyWord.keys():
                keyWord_file.write( key_id + ', ' ) 
                
        print "\tWriting into serialization files related to author_keyword."
        cPickle.dump(
            author_key_word_matrix,
            open(serialization_dir + author_key_word_matrix_file, "wb"), 2)
      
    return author_key_word_matrix


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
    name_statistics = load_name_statistic()
    (name_instance_dict, id_name_dict) = load_author_files(name_statistics)
    (author_paper_matrix, all_author_paper_matrix, coauthor_matrix, name_instance_dict, id_name_dict, author_paper_stat) = load_coauthor_files(name_instance_dict, id_name_dict)
    (covenue_matrix, author_venue_matrix) = load_covenue_files(id_name_dict, author_paper_matrix, all_author_paper_matrix)
    author_word_matrix = load_author_word_files(id_name_dict, author_paper_matrix)
    author_key_word_matrix = load_author_keyword_files(author_paper_matrix)

    metapaths = Metapaths(author_paper_matrix, author_venue_matrix, author_word_matrix, author_key_word_matrix, coauthor_matrix, covenue_matrix)
    return (name_instance_dict, id_name_dict, name_statistics, author_paper_stat, metapaths)


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
