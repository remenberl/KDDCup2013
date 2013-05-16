#-*- coding: UTF-8 -*
from custom_setting import *
from io import *
from recall_related import *
from precision_related import *


if __name__ == '__main__':
    print "Step 1/5: Load files"
    (name_instance_dict, id_name_dict, name_statistics,
        author_paper_matrix, coauthor_matrix,
        author_venue_matrix, covenue_matrix) = load_files()

    print "Step 2/5: Find similar ids to increase recall"
    add_similar_ids_under_name(name_instance_dict)

    print "Step 3/5: Create local clusters or potential_duplicate_groups"
    potential_duplicate_groups = create_potential_duplicate_groups(name_instance_dict)

    print "Step 4/5: Find and merge local clusters, then obtain the closure"
    real_duplicate_groups = local_clustering(potential_duplicate_groups, coauthor_matrix, covenue_matrix)
    authors_duplicates_dict = merge_local_clusters(real_duplicate_groups)
    find_closure(authors_duplicates_dict)

    print "Step 5/5: Generate submission files"
    save_result(authors_duplicates_dict, name_instance_dict, id_name_dict)
