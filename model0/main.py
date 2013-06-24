#-*- coding: UTF-8 -*
from custom_setting import *
from io import *
from recall_related import *
from precision_related import *
import cPickle

cannot_links = set()

def run_from_step(step):
    print "Step 1/6: Load files"
    (name_instance_dict, id_name_dict, name_statistics, author_paper_stat, author_good_paper_stat, metapaths) = load_files()
    print "\nStep 2/6: Find similar ids to increase recall"

    if step <= 2:
        add_similar_ids_under_name(name_instance_dict, id_name_dict, author_paper_stat)
    #     print "\tSaving files generated in this step for debug."
    #     cPickle.dump(
    #             name_instance_dict,
    #             open(serialization_dir + "final_" + name_instance_file, "wb"), 2)
    # else:
    #     print "\tLoading files generated from previous."
    #     name_instance_dict = cPickle.load(
    #             open(serialization_dir + 'final_' + name_instance_file, "rb"))

    print "\nStep 3/6: Create local clusters or potential_duplicate_groups"
    if step <= 3:
        potential_duplicate_groups = create_potential_duplicate_groups(name_instance_dict, author_paper_stat)

    #     print "\tSaving files generated in this step for debug."
    #     cPickle.dump(
    #             potential_duplicate_groups,
    #             open(serialization_dir + potential_duplicate_groups_file, "wb"), 2)
    # else:
    #     print "\tLoading files generated from previous."
    #     potential_duplicate_groups = cPickle.load(
    #             open(serialization_dir + potential_duplicate_groups_file, "rb"))
    
    print "\nStep 4/6: Find and merge local clusters"
    if step <= 4:
        metapaths.compute_coauthor()
        (real_duplicate_groups, similarity_score_dict, cannot_links) = local_clustering(potential_duplicate_groups, author_good_paper_stat, \
            name_instance_dict, id_name_dict, name_statistics, metapaths)
        print "\tSaving files generated in this step for debug."
    #     cPickle.dump(
    #             real_duplicate_groups,
    #             open(serialization_dir + '_' + real_duplicate_groups_file, "wb"), 2)
    #     cPickle.dump(
    #             similarity_score_dict,
    #             open(serialization_dir + '_' + similarity_score_dict_file, "wb"), 2)
    #     cPickle.dump(
    #             name_instance_dict,
    #             open(serialization_dir + "_merged_" + name_instance_file, "wb"), 2)
    #     cPickle.dump(
    #             id_name_dict,
    #             open(serialization_dir + "_merged_" + id_name_file, "wb"), 2)
    #     cPickle.dump(
    #             cannot_links,
    #             open(serialization_dir + cannot_links_file, "wb"), 2)
        
    # else:
    #     real_duplicate_groups = cPickle.load(
    #             open(serialization_dir + '_' + real_duplicate_groups_file, "rb"))
    #     similarity_score_dict = cPickle.load(
    #             open(serialization_dir + '_' + similarity_score_dict_file, "rb"))
    #     name_instance_dict = cPickle.load(
    #             open(serialization_dir + '_merged_' + name_instance_file, "rb"))
    #     id_name_dict = cPickle.load(
    #             open(serialization_dir + '_merged_' + id_name_file, "rb"))
    #     cannot_links = cPickle.load(
    #             open(serialization_dir + cannot_links_file, "rb"))
 
    print "\nStep 5/6: Obtain the closure, then filter noisy names"   
    authors_duplicates_dict = merge_local_clusters(real_duplicate_groups, id_name_dict)
    # pre_filter(authors_duplicates_dict, name_instance_dict, id_name_dict, similarity_score_dict, metapaths)
    find_closure(authors_duplicates_dict)
    refine_result(cannot_links, authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_score_dict, metapaths, True)
    iter_num = 3
    while iter_num > 0:
        find_closure(authors_duplicates_dict)
        refine_result(cannot_links, authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_score_dict, metapaths, True)
        iter_num -= 1
    # find_closure(authors_duplicates_dict)
    final_filter(authors_duplicates_dict, name_instance_dict, id_name_dict, author_paper_stat, similarity_score_dict, metapaths)

    print "\nStep 6/6: Generate submission files"
    save_result(authors_duplicates_dict, name_instance_dict, id_name_dict, similarity_score_dict)
       

if __name__ == '__main__':
    run_from_step(1)