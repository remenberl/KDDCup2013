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
    def __init__(self, AP, APV, APW, APK, AO, AY, APA, APVPA, APKPA, APAPA, APAPV):
        #AP: author-paper
        #APV: author-venue
        #APA: author-paper-venue
        #APVPA: author-venue-author
        #APW: author-word
        #APK: author-keyword
        #AO: author-orgnization
        self.AP = AP
        self.APV = APV
        self.APW = APW
        self.APK = APK
        self.AO = AO
        self.AY = AY
        self.APA = APA
        self.APVPA = APVPA
        self.APKPA = APKPA
        self.APAPA = APAPA
        self.APAPV = APAPV
         

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
                            if len(element) <= 3 and element != elements[-1]:
                                if name_statistics[element.lower()] <= 3: 
                                    new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                                elif element.lower() not in asian_units and element.lower() not in asian_last_names and name_statistics[element.lower()] <= 10:
                                    new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                                else:
                                    new_elements.append(element)
                            elif len(element) > 3 and name_statistics[element.lower()] <= 1:
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
            os.path.isfile(serialization_dir  + '2hop_' + coauthor_matrix_file) and \
            os.path.isfile(serialization_dir + author_paper_matrix_file) and \
            os.path.isfile(serialization_dir + 'all_' + author_paper_matrix_file) and \
            os.path.isfile(serialization_dir + 'complete_' + name_instance_file) and \
            os.path.isfile(serialization_dir + 'complete_' + id_name_file) and \
            os.path.isfile(serialization_dir + 'complete_' + author_paper_stat_file) :
        print "\tSerialization files related to coauthors exist."
        print "\tReading in the serialization files.\n"
        coauthor_matrix = cPickle.load(
            open(serialization_dir + coauthor_matrix_file, "rb"))
        coauthor_2hop_matrix = cPickle.load(
            open(serialization_dir + '2hop_' + coauthor_matrix_file, "rb"))
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
        # coauthor_2hop_matrix = author_paper_matrix * all_author_paper_matrix.transpose() * all_author_paper_matrix * all_author_paper_matrix.transpose()
        coauthor_2hop_matrix = coauthor_matrix * coauthor_matrix.transpose()
       
        # print "\tRemoving diagonal elements in coauthor_matrix."
        # coauthor_matrix = coauthor_matrix - spdiags(coauthor_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')
        # coauthor_2hop_matrix = coauthor_2hop_matrix - spdiags(coauthor_2hop_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')

        print "\tWriting into serialization files related to coauthors.\n"
        cPickle.dump(
            coauthor_matrix,
            open(serialization_dir + coauthor_matrix_file, "wb"), 2)
        cPickle.dump(
            coauthor_2hop_matrix,
            open(serialization_dir + '2hop_' + coauthor_matrix_file, "wb"), 2)
        cPickle.dump(
            author_paper_matrix,
            open(serialization_dir + author_paper_matrix_file, "wb"), 2)
        cPickle.dump(
            all_author_paper_matrix,
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
     
    # coauthor_3hop_matrix = coauthor_2hop_matrix * coauthor_matrix.transpose()

    return (author_paper_matrix, all_author_paper_matrix, coauthor_matrix, coauthor_2hop_matrix, name_instance_dict, id_name_dict, author_paper_stat)


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
    covenue_matrix = author_venue_matrix * author_venue_matrix.transpose()
    # print "\tRemoving diagonal elements in covenue_matrix.\n"
    # covenue_matrix = covenue_matrix - spdiags(covenue_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')

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


def load_author_keyword_files(author_paper_matrix, all_author_paper_matrix):
    if os.path.isfile(serialization_dir + author_key_word_matrix_file) and \
            os.path.isfile(serialization_dir + co_key_word_matrix_file):
        print "\tSerialization files related to author_keyword exist."
        print "\tReading in the serialization files."
        author_key_word_matrix = cPickle.load(open(
            serialization_dir + author_key_word_matrix_file, "rb"))
        co_key_word_matrix = cPickle.load(open(
            serialization_dir + co_key_word_matrix_file, "rb"))
    else:
        print "\tSerialization files related to author_keyword do not exist."
        nAuthor = author_paper_matrix.shape[0]-1
        nPaper = author_paper_matrix.shape[1]-1
        count = 0 #to count the # of unique key words
        dict_paper_keyWord = dict() #key: paperID. value: list of key words
        dict_keyWord = dict() #maps a keyWord to the corresponding column in paper_keyword_matrix
        word_count_dict = dict()

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
                                    word_count_dict[tmpWord] = word_count_dict.setdefault(tmpWord, 0) + 1
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
                if word_count_dict[word] > 1:
                    paper_keyword_matrix[paper_id, dict_keyWord[word]] += 1
        
        author_key_word_matrix = author_paper_matrix * paper_keyword_matrix 
        all_author_key_word_matrix = all_author_paper_matrix * paper_keyword_matrix

        co_key_word_matrix = author_key_word_matrix * all_author_key_word_matrix.transpose()
        # print "\tComputing the co-key-word graph."
        # co_keyword_matrix = author_key_word_matrix * author_key_word_matrix.transpose()
        # co_keyword_matrix = co_keyword_matrix - spdiags(co_keyword_matrix.diagonal(), 0, nAuthor+1, nAuthor+1, 'csr')

        #store unique key-words into txt file for manual check
        # with open("./data/list_paper_key_words.txt", 'wb') as keyWord_file:
        #     keyWord_file.write('Unique Key Words: n = ' + str(len(dict_keyWord)) + '\n')
        #     for key_id in dict_keyWord.keys():
        #         keyWord_file.write( key_id + ', ' ) 
                
        print "\tWriting into serialization files related to author_keyword."
        cPickle.dump(
            author_key_word_matrix,
            open(serialization_dir + author_key_word_matrix_file, "wb"), 2)
        cPickle.dump(
            co_key_word_matrix,
            open(serialization_dir + co_key_word_matrix_file, "wb"), 2)      
    return (author_key_word_matrix, co_key_word_matrix)


def load_author_affili_matrix_files():
    if os.path.isfile(serialization_dir + author_affli_matrix_file):
        print "\tSerialization files related to author_affiliation exist."
        print "\tReading in the serialization files.\n"
        author_affi_matrix = cPickle.load(open(
            serialization_dir + author_affli_matrix_file, "rb"))
    else:
        print "\tSerialization files related to author_affiliation do not exist."
        dict_author_affi = dict()
        dict_affi = dict()
        dict_affi_frequency = dict()
        cnt_affi = 1 
        cnt_line = 0

        with open(author_file, 'rb') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='"') 
            next(author_reader) 
            for row in author_reader:
                cnt_line += 1
                if cnt_line % 40000 == 0:
                    print "\tFinish analysing " + str(cnt_line) + " lines of the file."
                author_id = int(row[0])
                author_affili = row[2].strip().lower()
                if author_affili != '':
                    author_affilis = author_affili.replace(',', '|').replace('-','|').split('|')
                    for author_affili in author_affilis:
                        author_affili = author_affili.strip()
                        if author_affili == '':
                            continue
                        if author_affili not in dict_affi: 
                            dict_affi[author_affili] = cnt_affi
                            cnt_affi += 1
                            dict_affi_frequency[author_affili] = 1
                        else:
                            dict_affi_frequency[author_affili] += 1
                        if author_id not in dict_author_affi:
                            dict_author_affi[author_id] = [author_affili]
                        else:
                            dict_author_affi[author_id] += [author_affili]

        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"') 
            next(paper_author_reader) 
            for row in paper_author_reader:
                cnt_line += 1
                if cnt_line % 2000000 == 0:
                    print "\tFinish analysing " + str(cnt_line) + " lines of the file."
                author_id = int(row[1])
                author_affili = row[3].strip().lower()
                if author_affili != '':
                    author_affilis = author_affili.replace(',', '|').replace('-','|').split('|')
                    for author_affili in author_affilis:
                        author_affili = author_affili.strip()
                        if author_affili == '':
                            continue
                        if author_affili not in dict_affi:
                            dict_affi[author_affili] = cnt_affi
                            cnt_affi += 1
                            dict_affi_frequency[author_affili] = 1
                        else:
                            dict_affi_frequency[author_affili] += 1
                        if author_id not in dict_author_affi:
                            dict_author_affi[author_id] = [author_affili]
                        else:
                            dict_author_affi[author_id] += [author_affili]

        #nUniqueAffi is the number of unique affliations            
        nUniqueAffi = cnt_affi  

        #Create author-affiliation matrix
        print "\tCreating author-affiliation matrix."
        author_affi_matrix = lil_matrix( ( max_author+1, nUniqueAffi+1 ))
        for author_id in dict_author_affi.iterkeys():
            author_affi = dict_author_affi[author_id]
            for affi in author_affi: 
                author_affi_matrix[author_id, dict_affi[affi]] += 1
        
        author_affi_matrix = author_affi_matrix.tocsr()
        print "\tWriting into serialization files related to author_affi.\n"
        cPickle.dump(author_affi_matrix, \
                    open(serialization_dir + author_affli_matrix_file, "wb"), 2)
                    
        ## Summary: sorted_affi_freq and sorted_affiName
        #sort the frequency of each affiliation from high to low. 
        #sorted_affiName (a list) stores the corresponding affiliation names

        # sorted_affiName = sorted(dict_affi_frequency, key=dict_affi_frequency.get, reverse=True)
        # sorted_affi_freq = range(0, len(sorted_affiName))
        # for i in range(0, len(sorted_affiName)):
        #     sorted_affi_freq[i] = dict_affi_frequency[sorted_affiName[i]]  

        #you can see the frequency of a certain affiliation. 
        #Most common one is '' (none)
        #return (author_affi_matrix, sorted_affiName, sorted_affi_freq) 
        
    return author_affi_matrix


def load_author_year_matrix_files():
    if os.path.isfile(serialization_dir + author_year_matrix_file):
        print "\tSerialization files related to author_year exist."
        print "\tReading in the serialization files."
        author_year_matrix = cPickle.load(open(\
                            serialization_dir + author_year_matrix_file, "rb"))
            
    else:
        MinValidYear = 1900
        MaxValidYear = 2013
        nValidYearSpan = MaxValidYear - MinValidYear + 1

        dict_paper_year = dict()
        dict_author_year = dict()
        
        print "\tConstruct paperID-year dict"
        with open(paper_file, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                paper_id = int(row[0])
                year = int(row[2])
                if year >= MinValidYear and year <= MaxValidYear:
                    dict_paper_year[paper_id] = year

        print "\tConstruct author-year dict"
        cnt_line = 0
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"') 
            next(paper_author_reader) 
            for row in paper_author_reader:
                cnt_line += 1
                if cnt_line % 2000000 == 0:
                    print "\tFinish analysing " + str(cnt_line) + " lines of the file."
                paper_id = int(row[0])
                author_id = int(row[1])  
                if paper_id in dict_paper_year:
                    year = dict_paper_year[paper_id]
                    if author_id not in dict_author_year:
                        dict_author_year[author_id] = [year]
                    else:
                        dict_author_year[author_id] += [year]

        #Create author-year matrix
        print "\tCreating author-year matrix."
        author_year_matrix = lil_matrix( ( max_author+1, nValidYearSpan ))
        for author_id in dict_author_year.iterkeys():
            allYears = dict_author_year[author_id]
            for year in allYears:
                author_year_matrix[author_id, year - MinValidYear] += 1
        
        print "\tWriting into serialization files related to author_year."
        cPickle.dump(author_year_matrix, \
                    open(serialization_dir + author_year_matrix_file, "wb"), 2)
    
    return author_year_matrix
      


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
    (author_paper_matrix, all_author_paper_matrix, coauthor_matrix, coauthor_2hop_matrix, name_instance_dict, id_name_dict, author_paper_stat) = load_coauthor_files(name_instance_dict, id_name_dict)
    (covenue_matrix, author_venue_matrix) = load_covenue_files(id_name_dict, author_paper_matrix, all_author_paper_matrix)
    author_word_matrix = load_author_word_files(id_name_dict, author_paper_matrix)
    (author_key_word_matrix, co_key_word_matrix_file) = load_author_keyword_files(author_paper_matrix, all_author_paper_matrix)
    author_org_matrix = load_author_affili_matrix_files()
    author_year_matrix = load_author_year_matrix_files() 

    APAPC = coauthor_matrix * author_venue_matrix
    metapaths = Metapaths(author_paper_matrix, author_venue_matrix, author_word_matrix, author_key_word_matrix, author_org_matrix, author_year_matrix, coauthor_matrix, covenue_matrix, co_key_word_matrix_file, coauthor_2hop_matrix, APAPC)
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
