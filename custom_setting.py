#-*- coding: UTF-8 -*-

author_file = "./data/Author.csv"
paper_author_file = "./data/PaperAuthor.csv"
paper_file = './data/sanitizedPaper.csv'
stopword_file = './data/Stopword.csv'

duplicate_authors_file = "./result/duplicate_authors.csv"
duplicate_authors_full_name_file = "./result/duplicate_authors_fullname.csv"


merge_threshold = 0.000000001
word_title_count_threshold = 100

version = "v2_4"
serialization_dir = "./serialize/"
coauthor_matrix_file = "coauthor.seal" + '.' + version
covenue_matrix_file = "covenue.seal" + '.' + version
author_word_matrix_file = "author_word.seal" + '.' + version
author_venue_matrix_file = "author_venue.seal" + '.' + version
author_paper_matrix_file = "author_paper.seal" + '.' + version
name_instance_file = "name_instance.seal" + '.' + version
id_name_file = "id_name.seal" + '.' + version
name_statistics_file = "name_statistics.seal" + '.' + version
author_paper_stat_file = "author_paper_stat.seal" + '.' + version
potential_duplicate_groups_file = "potential_duplicate_groups.seal" + '.' + version
real_duplicate_groups_file = "real_duplicate_groups.seal" + '.' + version
similarity_score_dict_file = "similarity_score.seal" + '.' + version

max_conference = 5222
max_journal = 22228
max_author = 2293837
max_paper = 2259021
