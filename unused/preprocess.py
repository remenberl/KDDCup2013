
import csv
import os
import re
from difflib import SequenceMatcher
from name import *
from custom_setting import *
import cPickle
from precision_related import *


name_statistics = cPickle.load(
            open(serialization_dir + name_statistics_file, "rb"))

id_name_dict = dict()

def load_author_files():
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
            author = Name(row[1])
            id_name_dict[author_id] = [row[1], author]


def load_paper_author_files():
    print "\tReading in the paperauthor.csv file."
    with open(paper_author_file, 'rb') as csv_file:
        paper_author_reader = csv.reader(
            csv_file, delimiter=',', quotechar='"')
        # skip first line
        next(paper_author_reader)
        count = 0
        name_dict =dict()
        name_count = dict()
        for row in paper_author_reader:
            count += 1
            if count % 500000 == 0:
                print "\tFinish analysing " \
                    + str(count) + " lines of the file."
            if row[2].find('(') >= 0:
                continue
            author_id = int(row[1])
            if author_id in id_name_dict:
                name_dict.setdefault(author_id,set())
                tmp = Name(row[2], True)
                name_count[tmp.name] = name_count.setdefault(tmp.name, 0) + 1
                if row[2].strip() != '' and row[2] not in name_dict[author_id]:
                    author = Name(row[2])
                    author.original_name = row[2]
                    id_name_dict[author_id].append(author)
                    name_dict[author_id].add(row[2])
        # for (author_id, name_list) in id_name_dict.iteritems():
        #     if len(name_list) != 3 or name_count[name_list[2].name] < 2:
        #         id_name_dict[author_id] = id_name_dict[author_id][0:1]

            # new_name_list = list(name_list)
            # for name_instance in name_list[2:]:
            #     if lenname_list
                # if name_instance.name == '' or name_list[1].name == '':
                #     continue
                # if name_count[name_instance.name] < 2 or name_instance.first_name[0] != name_list[1].first_name[0] or name_instance.last_name != name_list[1].last_name:
                #     new_name_list.remove(name_instance)
                # elif name_instance.is_asian:
                #     new_name_list.remove(name_instance)
                # else:
                #     elements = name_list[1].name.split(' ')
                #     for element in elements:
                #         if name_instance.name.count(element) > 1:
                #             new_name_list.remove(name_instance)
                #             break
            # id_name_dict[author_id] = new_name_list

def recover():
    infer_name_dict = {}
    count = 0
    for (author_id, name_list) in id_name_dict.iteritems():
        comparable_names = list()
        if name_list[0].strip() == '':
            continue

        unit_num1 = len(name_list[1].name.split())
        if len(name_list) > 2:
            for name_instance1 in name_list[2:]:
                flag = False
                for name_instance2 in name_list[1:]:
                    if not name_comparable(name_instance2, name_instance1, name_statistics):
                        flag = True
                unit_num2 = len(name_instance1.name.split())
                if flag == False and unit_num2 >= unit_num1:
                    comparable_names.append(name_instance1.name)
            if len(comparable_names) == 0:
                continue
            candidate = max(comparable_names, key=len)
            if len(candidate) > 30:
                continue

            if name_list[1].name != candidate and len(candidate) > len(name_list[1].name):
                # if len(candidate.split()) > len(name_list[1].name.split()):
                for name_instance2 in name_list[1:]:
                    if name_instance2.name == candidate:
                        infer_name_dict[author_id] = name_instance2.original_name
                        print name_list[0] + str(" ---> ") + name_instance2.original_name + ' ' + str(author_id)
                        count += 1
                        break
    print count
    return infer_name_dict

if __name__ == '__main__':
    # load_author_files()
    # load_paper_author_files()
    # cPickle.dump(
    #         id_name_dict,
    #         open(serialization_dir + 'preprocess_' + id_name_file, "wb"), 2)

    id_name_dict = cPickle.load(
            open(serialization_dir + 'preprocess_' + id_name_file, "rb"))
    print 'begin'
    infer_name_dict = recover()

    with open('./data/Recovered_Author.csv', 'wb') as result_file:
        with open(author_file, 'rb') as author_file:
            for line in author_file:
                elements = line.split(',')
                if elements[0] == 'Id':
                    result_file.write(','.join(elements))
                    continue
                if int(elements[0]) in infer_name_dict:
                    elements[1] = infer_name_dict[int(elements[0])]
                result_file.write(','.join(elements))



