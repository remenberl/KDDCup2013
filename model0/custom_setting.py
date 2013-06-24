#-*- coding: UTF-8 -*-
author_file = "../data/Author_refined_simple.csv"
paper_author_file = "../data/PaperAuthor_refined_simple.csv"
paper_file = '../data/Paper.csv'
stopword_file = '../data/Stopword.csv'
confident_duplicate_authors_file = '../data/duplicate_authors.csv'

duplicate_authors_file = "../data/complete_duplicate_authors_2.csv"
duplicate_authors_full_name_file = "./result/duplicate_authors_fullname.csv"
duplicate_authors_unconfident_subset_file = "./result/duplicate_authors_unconfident_subset.csv"


merge_threshold = 0.00000000001
word_title_count_threshold = 1000000

version = "v3_0"
serialization_dir = "./serialize/"
coauthor_matrix_file = "coauthor.seal" + '.' + version
covenue_matrix_file = "covenue.seal" + '.' + version
co_key_word_matrix_file = "cokeyword.seal" + '.' + version
author_word_matrix_file = "author_word.seal" + '.' + version
author_venue_matrix_file = "author_venue.seal" + '.' + version
author_paper_matrix_file = "author_paper.seal" + '.' + version
author_key_word_matrix_file = "author_key_word.seal" + '.' + version
author_affli_matrix_file = "author_affli_matrix.seal" + '.' + version
author_year_matrix_file = "_author_year_matrix.seal" + '.' + version
name_instance_file = "name_instance.seal" + '.' + version
id_name_file = "id_name.seal" + '.' + version
name_statistics_file = "name_statistics.seal" + '.' + version
author_paper_stat_file = "author_paper_stat.seal" + '.' + version
potential_duplicate_groups_file = "potential_duplicate_groups.seal" + '.' + version
real_duplicate_groups_file = "real_duplicate_groups.seal" + '.' + version
similarity_score_dict_file = "similarity_score.seal" + '.' + version
cannot_links_file = "cannot_links.seal" + '.' + version

max_conference = 5222
max_journal = 22228
max_author = 2293837
max_paper = 2259021
