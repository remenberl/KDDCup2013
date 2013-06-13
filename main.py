#-*- coding: UTF-8 -*
from custom_setting import *
from io import *
from recall_related import *
from precision_related import *
import cPickle



def run_from_step(step):
    print "Step 1/6: Load files"
    (name_instance_dict, id_name_dict, name_statistics, author_paper_stat, metapaths) = load_files()
    print "\nStep 2/6: Find similar ids to increase recall"

    if step <= 2:
        add_similar_ids_under_name(name_instance_dict, id_name_dict)
        print "\tSaving files generated in this step for debug."
        cPickle.dump(
                name_instance_dict,
                open(serialization_dir + "final_" + name_instance_file, "wb"), 2)
    else:
        print "\tLoading files generated from previous."
        name_instance_dict = cPickle.load(
                open(serialization_dir + 'final_' + name_instance_file, "rb"))

    print "\nStep 3/6: Create local clusters or potential_duplicate_groups"
    if step <= 3:
        potential_duplicate_groups = create_potential_duplicate_groups(name_instance_dict, author_paper_stat)

        print "\tSaving files generated in this step for debug."
        cPickle.dump(
                potential_duplicate_groups,
                open(serialization_dir + potential_duplicate_groups_file, "wb"), 2)
    else:
        print "\tLoading files generated from previous."
        potential_duplicate_groups = cPickle.load(
                open(serialization_dir + potential_duplicate_groups_file, "rb"))

    print "\nStep 4/6: Find and merge local clusters"
    if step <= 4:
        similarity_score_dict = dict()
        real_duplicate_groups1 = local_clustering(similarity_score_dict, potential_duplicate_groups, author_paper_stat, \
            name_instance_dict, id_name_dict, name_statistics, metapaths)
        real_duplicate_groups2 = local_clustering(similarity_score_dict, potential_duplicate_groups, author_paper_stat, \
            name_instance_dict, id_name_dict, name_statistics, metapaths)
        real_duplicate_groups = real_duplicate_groups1.union(real_duplicate_groups2)
        print "\tSaving files generated in this step for debug."
        cPickle.dump(
                real_duplicate_groups,
                open(serialization_dir + real_duplicate_groups_file, "wb"), 2)
        cPickle.dump(
                similarity_score_dict,
                open(serialization_dir + similarity_score_dict_file, "wb"), 2)
        cPickle.dump(
                name_instance_dict,
                open(serialization_dir + "merged_" + name_instance_file, "wb"), 2)
        cPickle.dump(
                id_name_dict,
                open(serialization_dir + "merged_" + id_name_file, "wb"), 2)
    else:
        real_duplicate_groups = cPickle.load(
                open(serialization_dir + real_duplicate_groups_file, "rb"))
        similarity_score_dict = cPickle.load(
                open(serialization_dir + similarity_score_dict_file, "rb"))
        name_instance_dict = cPickle.load(
                open(serialization_dir + 'merged_' + name_instance_file, "rb"))
        id_name_dict = cPickle.load(
                open(serialization_dir + 'merged_' + id_name_file, "rb"))
 

    print "\nStep 5/6: Obtain the closure, then filter noisy names"   
    if step <= 5:
        authors_duplicates_dict = merge_local_clusters(real_duplicate_groups, id_name_dict)
        # pre_filter(authors_duplicates_dict, name_instance_dict, id_name_dict, similarity_score_dict, metapaths)
        find_closure(authors_duplicates_dict)
        refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_score_dict, metapaths, True)
        iter_num = 2
        while iter_num > 0:
            find_closure(authors_duplicates_dict)
            refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_score_dict, metapaths, True)
            iter_num -= 1

        print "\tSaving files generated in this step for debug."
        cPickle.dump(
                authors_duplicates_dict,
                open(serialization_dir + analyzed_duplicate_groups_file, "wb"), 2)
        cPickle.dump(
                similarity_score_dict,
                open(serialization_dir + similarity_score_dict_file, "wb"), 2)
    else:
        authors_duplicates_dict = cPickle.load(
                open(serialization_dir + analyzed_duplicate_groups_file, "rb"))
        similarity_score_dict = cPickle.load(
                open(serialization_dir + similarity_score_dict_file, "rb"))

    print "\nStep 6/7: Final filtering and combining multiple possible guessing"
    final_filter(author_paper_stat, name_statistics, authors_duplicates_dict, name_instance_dict, id_name_dict, similarity_score_dict, metapaths)

    print "\nStep 7/7: Generate submission files"
    save_result(authors_duplicates_dict, name_instance_dict, id_name_dict)
       

if __name__ == '__main__':
    run_from_step(4)