#-*- coding: UTF-8 -*-

author_file = "./data/Author.csv"
paper_author_file = "./data/PaperAuthor.csv"
paper_file = './data/sanitizedPaper.csv'
stopword_file = './data/Stopword.csv'

duplicate_authors_file = "./result/duplicate_authors.csv"
duplicate_authors_full_name_file = "./result/duplicate_authors_fullname.csv"


sequence_matcher_threshold = 0.8
coauthor_weight = 100
author_venue_weight = 10
covenue_weight = 10
paper_word_weight = 10
merge_threshold = 0.000000001
word_title_count_threshold = 100

serialization_dir = "./serialize/"
coauthor_matrix_file = "coauthor.seal.v1"
covenue_matrix_file = "covenue.seal.v1"
author_word_matrix_file = "author_word.seal.v1"
author_paper_matrix_file = "author_paper.seal.v1"
name_instance_file = "name_instance.seal.v1"
id_name_file = "id_name.seal.v1"
name_statistics_file = "name_statistics.seal.v1"

max_conference = 5222
max_journal = 22228
max_author = 2293837
max_paper = 2259021
