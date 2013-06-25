#-*- coding: UTF-8 -*-
import csv
import os
import cPickle
import re
from scipy.sparse import lil_matrix, dok_matrix, spdiags
from difflib import SequenceMatcher
from name import *
from custom_setting import *
import re

duplicate_author_dict = dict()

class Metapaths(object):
    """docstring for ClassName"""
    def __init__(self, AP, APV, AO):
        #AP: author-paper
        #APV: author-venue
        #APA: author-paper-venue
        #APVPA: author-venue-author
        #APW: author-word
        #APK: author-keyword
        #AO: author-orgnization
        self.AP = AP
        self.APV = APV
        self.AO = AO

    def compute_coauthor(self):
        print "\tComputing the coauthor graph."
        self.APA = self.AP * self.AP.transpose()


def load_name_statistic():
    directory = os.path.dirname(serialization_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.isfile(serialization_dir + name_statistics_file) and \
            os.path.isfile(serialization_dir + 'super_' + name_statistics_file) and \
            os.path.isfile(serialization_dir + 'raw_' + name_statistics_file) and \
            os.path.isfile(serialization_dir + 'complete_' + author_paper_stat_file) and\
            os.path.isfile(serialization_dir + 'good_' + author_paper_stat_file):
        print "\tSerialization files related to name_statistics exist."
        print "\tReading in the serialization files.\n"
        name_statistics = cPickle.load(
            open(serialization_dir + name_statistics_file, "rb"))
        name_statistics_super = cPickle.load(
            open(serialization_dir + 'super_' + name_statistics_file, "rb"))
        raw_name_statistics = cPickle.load(
            open(serialization_dir + 'raw_' + name_statistics_file, "rb"))
        author_paper_stat = cPickle.load(
            open(serialization_dir + 'complete_' + author_paper_stat_file, "rb"))
        author_good_paper_stat = cPickle.load(
            open(serialization_dir + 'good_' + author_paper_stat_file, "rb"))
    else:
        print "\tSerialization files related to name_statistics do not exist."
        name_statistics = dict()
        raw_name_statistics = dict()
        name_statistics_super = dict()
        author_paper_stat = dict()
        author_good_paper_stat = dict()
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
                elements = author_name.split()
                for element in elements:
                    if element != '':
                        raw_name_statistics[element] = raw_name_statistics.setdefault(element, 0) + 1
                author_name = re.sub('[^a-zA-Z ]', '', author_name)
                elements = author_name.split()
                for element in elements:
                    if element != '':
                        name_statistics[element] = name_statistics.setdefault(element, 0) + 1
                        name_statistics_super[element] = name_statistics.setdefault(element, 0) + 1
                for element1 in elements:
                    for element2 in elements:
                        if element1 != element2:
                            name_statistics[element1 + ' ' + element2] = name_statistics.setdefault(element1 + ' ' + element2, 0) + 1
                            # name_statistics[element2 + ' ' + element1] = name_statistics.setdefault(element2 + ' ' + element1, 0) + 1
                            name_statistics_super[element1 + ' ' + element2] = name_statistics_super.setdefault(element1 + ' ' + element2, 0) + 1
                            # name_statistics_super[element2 + ' ' + element1] = name_statistics_super.setdefault(element2 + ' ' + element1, 0) + 1
        print "\tReading in the paperauthor.csv file."

        paper_quality_score = dict()
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
                try:
                    author_name = row[2].lower().strip()
                except Exception, e:
                    print row
                
                author_name = re.sub('[^a-zA-Z ]', '', author_name)
                author_id = int(row[1])
                paper_id = int(row[0])
                paper_quality_score[paper_id] = paper_quality_score.setdefault(paper_id, 0) + 1
                if row[3].strip() != '':
                    paper_quality_score[paper_id] += 1

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
                try:
                    author_name = row[2].lower().strip()
                except Exception, e:
                    print row
                
                author_name = re.sub('[^a-zA-Z ]', '', author_name)
                author_id = int(row[1])
                paper_id = int(row[0])
                if paper_quality_score[paper_id] > 1:
                    author_good_paper_stat[author_id] = author_good_paper_stat.setdefault(author_id, 0) + 1
                author_paper_stat[author_id] = author_paper_stat.setdefault(author_id, 0) + 1
                elements = author_name.split()
                for element in elements:
                    if element != '':
                        name_statistics_super[element] = name_statistics.setdefault(element, 0) + 1
                for element1 in elements:
                    for element2 in elements:
                        if element1 != element2:
                            name_statistics_super[element1 + ' ' + element2] = name_statistics_super.setdefault(element1 + ' ' + element2, 0) + 1
                            # name_statistics_super[element2 + ' ' + element1] = name_statistics_super.setdefault(element2 + ' ' + element1, 0) + 1
        print "\tWriting into serialization files related to name_statistics.\n"
        cPickle.dump(
            name_statistics,
            open(serialization_dir + name_statistics_file, "wb"), 2)
        cPickle.dump(
            raw_name_statistics,
            open(serialization_dir + 'raw_' + name_statistics_file, "wb"), 2)
        cPickle.dump(
            name_statistics_super,
            open(serialization_dir + 'super_' + name_statistics_file, "wb"), 2)
        cPickle.dump(
            author_paper_stat,
            open(serialization_dir + 'complete_' + author_paper_stat_file, "wb"), 2)
        cPickle.dump(
            author_good_paper_stat,
            open(serialization_dir + 'good_' + author_paper_stat_file, "wb"), 2)
    return (name_statistics, raw_name_statistics, name_statistics_super, author_paper_stat, author_good_paper_stat)


def load_author_files(name_statistics,  raw_name_statistics, name_statistics_super, author_paper_stat):
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
        name_statistics = cPickle.load(
            open(serialization_dir + name_statistics_file, "rb"))
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

                elements = author_name.split()
                if author_name.upper()[:-1] == author_name[:-1]:
                    new_elements = elements
                else:
                    new_elements = list()
                    for element in elements:
                        if element.lower() in raw_name_statistics:
                            if len(element) <= 3 and element != elements[-1]:
                                if raw_name_statistics[element.lower()] <= 3: 
                                    new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                                elif element.lower() not in asian_units and element.lower() not in asian_last_names and raw_name_statistics[element.lower()] <= 10:
                                    new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                                else:
                                    new_elements.append(element)
                            elif len(element) > 3 and raw_name_statistics[element.lower()] <= 1:
                                if element.lower()[:-1] not in raw_name_statistics or raw_name_statistics[element.lower()[:-1]] <= 1:
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

        # add other authors together with authors in paperauthor.csv
        paper_quality_score = dict()
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
                try:
                    author_name = row[2].lower().strip()
                except Exception, e:
                    print row
                
                author_name = re.sub('[^a-zA-Z ]', '', author_name)
                author_id = int(row[1])
                paper_id = int(row[0])
                paper_quality_score[paper_id] = paper_quality_score.setdefault(paper_id, 0) + 1
                if row[3].strip() != '':
                    paper_quality_score[paper_id] += 1


        paper_subset = set()
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
                if author_id in id_name_dict and paper_id in paper_quality_score and paper_quality_score[paper_id] >= 3:
                    paper_subset.add(paper_id)
        other_author_set = set()
        other_names_dict = dict()        
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            #skip first line
            next(paper_author_reader)
            count = 0
            for row in paper_author_reader:
                count += 1
                if count % 500000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
                paper_id = int(row[0])
                author_id = int(row[1])
                if paper_id in paper_subset and author_id not in id_name_dict and author_paper_stat[author_id] >= 5:
                    other_author_set.add(author_id)

        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            #skip first line
            next(paper_author_reader)
            count = 0
            for row in paper_author_reader:
                count += 1
                if count % 500000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
                author_id = int(row[1])
                if author_id in other_author_set:
                    author_name = row[2]
                    other_names_dict.setdefault(author_id, list()).append(author_name.strip())

        for (author_id, name_list) in other_names_dict.iteritems():
            author_name = max(name_list, key=name_list.count)
            elements = author_name.split()
            if author_name.upper()[:-1] == author_name[:-1]:
                new_elements = elements
            else:
                new_elements = list()
                for element in elements:
                    if element.lower() in raw_name_statistics:
                        if len(element) <= 3 and element != elements[-1]:
                            if raw_name_statistics[element.lower()] <= 3: 
                                new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                            elif element.lower() not in asian_units and element.lower() not in asian_last_names and raw_name_statistics[element.lower()] <= 10:
                                new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                            else:
                                new_elements.append(element)
                        elif len(element) > 3 and raw_name_statistics[element.lower()] <= 1:
                            if element.lower()[:-1] not in raw_name_statistics or raw_name_statistics[element.lower()[:-1]] <= 1:
                                new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                            else:
                                new_elements.append(element)
                        else:
                            new_elements.append(element)
                    else:
                        new_elements.append(element)
            author = Name(' '.join(new_elements))
            id_name_dict[author_id] = [author.name, author_name]
            if author.name in name_instance_dict:
                name_instance_dict[author.name].add_author_id(author_id)
            else:
                author.add_author_id(author_id)
                name_instance_dict[author.name] = author

        print '\tStart breaking names'
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
                author_name = row[1].strip()
                if author_name == '':
                    continue
                elements = author_name.split()
                new_elements = list()
                if len(elements[0]) > 1 and len(elements[0]) <= 5 and raw_name_statistics[elements[0].lower()] <= 20:
                    new_elements.append(re.sub(r"(?<=\w)([a-zA-Z])", r" \1", elements[0]))
                    for element in elements[1:]:
                        new_elements.append(element)
                    author = Name(' '.join(new_elements))
                    if author.name in name_instance_dict:
                        # print author_name + ' --> ' + author.name 
                        name_instance_dict[id_name_dict[author_id][0]].del_author_id(int(row[0]))
                        id_name_dict[author_id] = [author.name, row[1]]
                        if author.name in name_instance_dict:
                            name_instance_dict[author.name].add_author_id(int(row[0]))
                        else:
                            author.add_author_id(int(row[0]))
                            name_instance_dict[author.name] = author
        
        with open('log.txt', 'wb') as log_file:
            for name in list(name_instance_dict.iterkeys()):
                if name not in name_instance_dict:
                    continue
                name_instance = name_instance_dict[name]
                count += 1
                if count % 20000 == 0:
                        print "\tFinish analysing " \
                            + str(count) + " lines of the file for removing noisy last names."
                if len(name_instance.author_ids) == 1 and not name_instance.is_asian and not name_instance.has_dash:
                    elements = name_instance.name.split()
                    if len(elements) >= 2:
                        # if (elements[-2] + ' ' + elements[-1]) in name_statistics_super:
                        #     paper_num = 0
                        #     for id in name_instance.author_ids:
                        #         if id in author_paper_stat:
                        #             paper_num += author_paper_stat[id]
                        #     if paper_num != 0:
                        #         if name_statistics_super[(elements[-2] + ' ' + elements[-1])] / (paper_num + 0.0) > 0.2 or \
                        #                 name_statistics_super[(elements[-2] + ' ' + elements[-1])] >= 5:
                        #             continue
                        #     else:
                        #         continue
                        if (elements[-2] + ' ' + elements[-1]) in name_statistics_super and name_statistics_super[(elements[-2] + ' ' + elements[-1])] >= 2:
                            continue
                    i = len(name) / 3
                    flag = False
                    for j in range(1, i):
                        elements = name[:-j].split()
                        if len(elements) < 2:
                            break
                        if len(elements) <= 4:
                            pool = itertools.permutations(elements)
                        else:
                            pool = [elements]
                        for permutation in pool:
                            candi = ' '.join(permutation)
                            if candi in name_instance_dict:
                                if len(candi) <= 10 or len(name[:-j].split()[-1]) == 1:
                                    continue
                                if len(name_instance_dict[candi].author_ids) > len(name_instance.author_ids):
                                    for id in name_instance.author_ids:
                                        name_instance_dict[candi].add_author_id(id)
                                        id_name_dict[id][0] = candi
                                    alternatives = name_instance_dict[name].get_alternatives()
                                    for alternative in alternatives:
                                        name_instance_dict[candi].add_alternative(alternative)
                                    del name_instance_dict[name]
                                    log_file.write("\t\t" + name + ' --> ' + candi + '\n')
                                elif len(name_instance_dict[candi].author_ids) < len(name_instance.author_ids):
                                    for id in name_instance_dict[candi].author_ids:
                                        name_instance.add_author_id(id)
                                        id_name_dict[id][0] = name_instance.name
                                    alternatives = name_instance_dict[candi].get_alternatives()
                                    for alternative in alternatives:
                                        name_instance_dict[name].add_alternative(alternative)
                                    del name_instance_dict[candi]
                                    log_file.write("\t\t" + candi + ' --> ' + name + '\n')
                                else:
                                    score_A = 0
                                    elements = name.split()
                                    for k in xrange(len(elements) - 1):
                                        if (elements[k] + ' ' + elements[k + 1]) in name_statistics:
                                            score_A += name_statistics[elements[k] + ' ' + elements[k + 1]]
                                    if len(elements) == 1:
                                        score_A = 0
                                    else:
                                        score_A /= len(elements) - 1.0
                                    score_B = 0
                                    elements = candi.split()
                                    for k in xrange(len(elements) - 1):
                                        if (elements[k] + ' ' + elements[k + 1]) in name_statistics:
                                            score_B += name_statistics[elements[k] + ' ' + elements[k + 1]]
                                    if len(elements) == 1:
                                        score_B = 0
                                    else:
                                        score_B /= len(elements) - 1.0
                                    if score_A == score_B:
                                        score_A = 0
                                        score_B = 0
                                        if name_instance.last_name in name_statistics:
                                            score_A = name_statistics[name_instance.last_name]
                                        if name_instance_dict[candi].last_name in name_statistics:
                                            score_B = name_statistics[name_instance_dict[candi].last_name]
                                    if score_A <= score_B:
                                        for id in name_instance.author_ids:
                                            name_instance_dict[candi].add_author_id(id)
                                            id_name_dict[id][0] = candi
                                        alternatives = name_instance_dict[name].get_alternatives()
                                        for alternative in alternatives:
                                            name_instance_dict[candi].add_alternative(alternative)
                                        del name_instance_dict[name]
                                        log_file.write("\t\t" + str(score_A) + name + ' --> ' + str(score_B) + candi + '\n')
                                    else:
                                        for id in name_instance_dict[candi].author_ids:
                                            name_instance.add_author_id(id)
                                            id_name_dict[id][0] = name_instance.name
                                        alternatives = name_instance_dict[candi].get_alternatives()
                                        for alternative in alternatives:
                                            name_instance_dict[name].add_alternative(alternative)
                                        del name_instance_dict[candi]
                                        log_file.write("\t\t" + str(score_B) + candi + ' --> ' + str(score_A) + name + '\n')
                                flag = True
                                break
                        if flag == True:
                            break
         
        for name_instance in list(name_instance_dict.itervalues()):
            count += 1
            if count % 20000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
            if len(name_instance.name) < 10:
                continue
            new_elements = list()
            change_flag = False
            elements = name_instance.name.split()
            for element in elements:
                if len(element) > 10:
                    new_elements.append(element)
                    if element in name_statistics:
                        if name_statistics[element] >= 2:
                            continue
                    for i in range(4, len(element) - 4):
                        if element[:i] in name_statistics and element[i:] in name_statistics:
                            if element not in name_statistics or min(name_statistics[element[i:]], name_statistics[element[:i]]) > name_statistics[element] and\
                                    element[:i] not in asian_units and element[i:] not in asian_units and\
                                    (element[:i] + ' ' + element[i:]) in name_statistics:
                                new_elements.pop()
                                new_elements.append(element[:i])
                                new_elements.append(element[i:])
                                change_flag = True
                                break
                else:
                    new_elements.append(element)
            if change_flag == True:
                author = Name(' '.join(new_elements))
                if author.name != name_instance.name:
                    print '\t\tSplit ' + name_instance.name + ' --> ' +  author.name
                for id in name_instance.author_ids:
                    author.add_author_id(id)
                    id_name_dict[id][0] = author.name
                name_instance_dict[author.name] = author

        name_statistics = dict()
        for name_instance in list(name_instance_dict.itervalues()):
            elements = name_instance.name.split()
            for element in elements:
                name_statistics[element] = name_statistics.setdefault(element, 0) + len(name_instance.author_ids)
            for element1 in elements:
                    for element2 in elements:
                        if element1 != element2:
                            name_statistics[element1 + ' ' + element2] = name_statistics.setdefault(element1 + ' ' + element2, 0) + len(name_instance.author_ids)
                            # name_statistics[element2 + ' ' + element1] = name_statistics.setdefault(element2 + ' ' + element1, 0) + len(name_instance.author_ids)

        print "\tWriting into serialization files related to name_statistics.\n"
        cPickle.dump(
            name_statistics, 
            open(serialization_dir + name_statistics_file, "wb"), 2)
        print "\tWriting into serialization files related to authors.\n"
        cPickle.dump(
            name_instance_dict,
            open(serialization_dir + name_instance_file, "wb"), 2)
        cPickle.dump(
            id_name_dict,
            open(serialization_dir + id_name_file, "wb"), 2)
 
    return (name_instance_dict, id_name_dict, name_statistics)


def load_coauthor_files(name_instance_dict, id_name_dict, author_paper_stat):
    if os.path.isfile(serialization_dir + author_paper_matrix_file) and \
            os.path.isfile(serialization_dir + 'complete_' + name_instance_file) and \
            os.path.isfile(serialization_dir + 'complete_' + id_name_file):
        print "\tSerialization files related to coauthors exist."
        print "\tReading in the serialization files.\n"
        author_paper_matrix = cPickle.load(
            open(serialization_dir + author_paper_matrix_file, "rb"))
        name_instance_dict = cPickle.load(
            open(serialization_dir + 'complete_' + name_instance_file, "rb"))
        id_name_dict = cPickle.load(
            open(serialization_dir + 'complete_' + id_name_file, "rb"))
    else:
        if os.path.isfile(confident_duplicate_authors_file):
            print "\tReading from confident duplicate_author file."
            with open(confident_duplicate_authors_file, 'rb') as csv_file:
                duplicate_author_reader = csv.reader(
                        csv_file, delimiter=',', quotechar='"')
                next(duplicate_author_reader)
                count = 0
                for row in duplicate_author_reader:
                    count += 1
                    if count % 10000 == 0:
                        print "\tFinish reading in  "  \
                                + str(count) + " lines of the file."
                    author_list = row[1].split()
                    for author_id in author_list:
                        duplicate_author_dict.setdefault(int(row[0]), set()).add(int(author_id))
        print "\tSerialization files related to coauthors do not exist."
        # The maximum id for author is 2293837 and for paper is 2259021
        all_author_paper_matrix = lil_matrix((max_author + 1, max_paper + 1))
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
                if count % 500000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
                paper_id = int(row[0])
                author_id = int(row[1])
                all_author_paper_matrix[author_id, paper_id] = 1
                if author_id in duplicate_author_dict:
                    for id in duplicate_author_dict[author_id]:
                        all_author_paper_matrix[id, paper_id] = 1
                if author_id in id_name_dict:
                    author = Name(row[2], True)
                    author_paper_matrix[author_id, paper_id] = 1
                    if author_id in duplicate_author_dict:
                        for id in duplicate_author_dict[author_id]:
                            author_paper_matrix[id, paper_id] = 1
                    # add names appeared in paperauthor.csv
                    if author.last_name == name_instance_dict[id_name_dict[author_id][0]].last_name:
                        name_instance_dict[id_name_dict[author_id][0]].add_alternative(author.name)
                        id_name_dict[author_id].append(author.name)
                    elif SequenceMatcher(None, author.name, id_name_dict[author_id][0]).ratio() >= 0.6:
                        name_instance_dict[id_name_dict[author_id][0]].add_alternative(author.name)
                        id_name_dict[author_id].append(author.name)

        print "\tWriting into serialization files related to coauthors.\n"
        cPickle.dump(
            author_paper_matrix,
            open(serialization_dir + author_paper_matrix_file, "wb"), 2)
        cPickle.dump(
            name_instance_dict,
            open(serialization_dir + 'complete_' + name_instance_file, "wb"), 2)
        cPickle.dump(
            id_name_dict,
            open(serialization_dir + 'complete_' + id_name_file, "wb"), 2)
 
    return (author_paper_matrix, name_instance_dict, id_name_dict)


def load_covenue_files(id_name_dict, author_paper_matrix):
    if os.path.isfile(serialization_dir + author_venue_matrix_file):
        print "\tSerialization files related to author_venue exist."
        print "\tReading in the serialization files.\n"
        author_venue_matrix = cPickle.load(open(
            serialization_dir + author_venue_matrix_file, "rb"))
    else:
        print "\tSerialization files related to author_venue do not exist."
        # The maximum id for journal is 5222 and for conference is 22228
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
        
        print "\tWriting into serialization files related to author_venue.\n"
        cPickle.dump(
            author_venue_matrix,
            open(serialization_dir + author_venue_matrix_file, "wb"), 2)
       
    # print "\tRemoving diagonal elements in covenue_matrix.\n"
    # covenue_matrix = covenue_matrix - spdiags(covenue_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')

    return author_venue_matrix

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
        cnt_affi = 1
        cnt_line = 0
        word_count = {}
        with open(author_file, 'rb') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='"') 
            next(author_reader) 
            for row in author_reader:
                author_affili = row[2].strip().lower()
                author_affilis = re.sub('[^a-zA-Z ]', ' ', author_affili)
                words = author_affilis.split()
                for word in words:
                    if word != '':
                        word_count[word] = word_count.setdefault(word, 0) + 1
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"') 
            next(paper_author_reader) 
            for row in paper_author_reader:
                cnt_line += 1
                if cnt_line % 2000000 == 0:
                    print "\tFinish analysing " + str(cnt_line) + " lines of the file."
                author_id = int(row[1])
                author_affili = row[3].strip().lower()
                author_affilis = re.sub('[^a-zA-Z ]', ' ', author_affili)
                words = author_affilis.split()
                for word in words:
                    if word != '':
                        word_count[word] = word_count.setdefault(word, 0) + 1

        word_list = list(word_count.iterkeys())
        for word in word_list:
            if word_count[word] > 10000:
                del word_count[word]
        sorted_ = sorted(word_count.items(), key=lambda x: -x[1])
        print sorted_[0:20]
        with open(author_file, 'rb') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='"') 
            next(author_reader) 
            for row in author_reader:
                cnt_line += 1
                if cnt_line % 40000 == 0:
                    print "\tFinish analysing " + str(cnt_line) + " lines of the file."
                author_id = int(row[0])
                if author_id in duplicate_author_dict:
                    duplicate_authors = duplicate_author_dict[author_id]
                else:
                    duplicate_authors = list()
                author_affili = row[2].strip().lower()
                if author_affili != '':
                    author_affilis = re.sub('[^a-zA-Z ]', ' ', author_affili)
                    words = author_affilis.split()
                    for word in words:
                        if word == '':
                            continue
                        if word in word_count:
                            if word not in dict_affi: 
                                dict_affi[word] = cnt_affi
                                cnt_affi += 1
                                dict_author_affi.setdefault(author_id, list()).append(word)
                                for id in duplicate_authors:
                                    dict_author_affi.setdefault(id, list()).append(word)
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"') 
            next(paper_author_reader) 
            for row in paper_author_reader:
                cnt_line += 1
                if cnt_line % 2000000 == 0:
                    print "\tFinish analysing " + str(cnt_line) + " lines of the file."
                author_id = int(row[1])
                if author_id in duplicate_author_dict:
                    duplicate_authors = duplicate_author_dict[author_id]
                else:
                    duplicate_authors = list()
                author_affili = row[3].strip().lower()
                if author_affili != '':
                    author_affilis = re.sub('[^a-zA-Z ]', ' ', author_affili)
                    words = author_affilis.split()
                    for word in words:
                        if word == '':
                            continue
                        if word in word_count:
                            if word not in dict_affi:
                                dict_affi[word] = cnt_affi
                                cnt_affi += 1
                            dict_author_affi.setdefault(author_id, list()).append(word)
                            for id in duplicate_authors:
                                dict_author_affi.setdefault(id, list()).append(word)
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
        
    return author_affi_matrix


def load_files():
    (name_statistics, raw_name_statistics, name_statistics_super, author_paper_stat, author_good_paper_stat) = load_name_statistic()
    (name_instance_dict, id_name_dict, name_statistics) = load_author_files(name_statistics, raw_name_statistics, name_statistics_super, author_paper_stat)
    (author_paper_matrix, name_instance_dict, id_name_dict) = load_coauthor_files(name_instance_dict, id_name_dict, author_paper_stat)
    author_venue_matrix = load_covenue_files(id_name_dict, author_paper_matrix)
    author_org_matrix = load_author_affili_matrix_files()

    metapaths = Metapaths(author_paper_matrix, author_venue_matrix, author_org_matrix)
    return (name_instance_dict, id_name_dict, name_statistics, author_paper_stat, author_good_paper_stat, metapaths)


def save_result(authors_duplicates_dict, name_instance_dict, id_name_dict, similarity_dict):
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
    directory = os.path.dirname(duplicate_authors_full_name_file)
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

    with open(duplicate_authors_unconfident_subset_file, 'wb') as result_file:
        for author_id in sorted(authors_duplicates_dict.iterkeys()):
            id_list = sorted(authors_duplicates_dict[author_id])
            for id in id_list:
                if tuple(sorted((author_id, id))) in similarity_dict \
                        and similarity_dict[tuple(sorted((author_id, id)))] <= merge_threshold:
                    break
            else:
                continue
            result_file.write(id_name_dict[author_id][1]
                              + ' ' + str(author_id))
            id_list = sorted(authors_duplicates_dict[author_id])
            for id in id_list:
                if tuple(sorted((author_id, id))) in similarity_dict \
                        and similarity_dict[tuple(sorted((author_id, id)))] <= merge_threshold:
                    result_file.write(', *' + id_name_dict[id][1] + ' ' + str(id))
                else:
                    result_file.write(', ' + id_name_dict[id][1] + ' ' + str(id))
            result_file.write('\n')

