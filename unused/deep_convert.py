#-*- coding: UTF-8 -*-
import cPickle
import os
from custom_setting import *
import difflib
import re
import string
import unicodedata
import gc
from string import maketrans 
from operator import itemgetter, attrgetter

def __split_and_store(s, tokens_freq):
    s = s.lower()
    author_names = re.split('[ ]', s)
    for name in author_names:
        if name in tokens_freq:
            tokens_freq[name] = tokens_freq[name] + 1
        else:
            tokens_freq[name] = 1   
        
def load_token_freq():
    all_tokens_file = 'all_tokens.sel'
    if os.path.isfile(serialization_dir + all_tokens_file):
        print "Deserialize author name tokens"
        tokens_freq = cPickle.load(
            open(serialization_dir + all_tokens_file, "rb"))
    else:
        print "Serialize author name tokens"
        tokens_freq = {}    
        with open("data/Author.csv") as author_file:
            for line in author_file:
                tokens = line.split(',')
                if len(tokens) > 1:
                    __split_and_store(tokens[1], tokens_freq)
        with open("data/PaperAuthor.csv") as pa_file:
            for line in pa_file:
                tokens = line.split(',')
                if len(tokens) > 2:
                    __split_and_store(tokens[2], tokens_freq)
        cPickle.dump(
            tokens_freq,
            open(serialization_dir + all_tokens_file, "wb"), 2)
    
    return tokens_freq

def load_refined_token_freq():
    all_tokens_file = 'all_refined_tokens.sel'
    all_names_file = 'all_refined_names.sel'
    if os.path.isfile(serialization_dir + all_tokens_file) and \
       os.path.isfile(serialization_dir + all_names_file):
        print "Deserialize refined author name tokens"
        refined_tokens_freq = cPickle.load(
            open(serialization_dir + all_tokens_file, "rb"))
        refined_whole_name_freq = cPickle.load(
            open(serialization_dir + all_names_file, "rb"))
    else:
        print "Serialize refined author name tokens"
        refined_tokens_freq = {}    
        refined_whole_name_freq = {}    
        with open("data/Author_refined_simple.csv") as author_file:
            for line in author_file:
                tokens = line.split(',')
                if len(tokens) > 1:
                    name = tokens[1].lower()
                    if name in refined_whole_name_freq:
                        refined_whole_name_freq[name] += 1
                    else:
                        refined_whole_name_freq[name] = 1
                    __split_and_store(name, refined_tokens_freq)
        with open("data/PaperAuthor_refined_simple.csv") as pa_file:
            for line in pa_file:
                tokens = line.split(',')
                if len(tokens) > 2:
                    name = tokens[2].lower()
                    if name in refined_whole_name_freq:
                        refined_whole_name_freq[name] += 1
                    else:
                        refined_whole_name_freq[name] = 1
                    __split_and_store(name, refined_tokens_freq)
        cPickle.dump(
            refined_tokens_freq,
            open(serialization_dir + all_tokens_file, "wb"), 2)
    
        cPickle.dump(
            refined_whole_name_freq,
            open(serialization_dir + all_names_file, "wb"), 2)
    return refined_tokens_freq,refined_whole_name_freq

def generate_new_author_names():
    author_fn = 'data/Author_refined.csv'
    paper_author_fn = 'data/PaperAuthor_refined.csv'
    if not os.path.isfile(author_fn):
        done = {}
        print "Generating Author_refined.csv and PaperAuthor_refined.csv"
        with open("data/Author.csv") as author_file:
            f = open(author_fn, 'w')
            for line in author_file:
                tokens = line.split(',')
                if len(tokens) > 1:
                    if tokens[1] in done:
                        tokens[1] = done[tokens[1]]
                    else:
                        clean = remove_noise(tokens[1])
                        done[tokens[1]] = clean
                        tokens[1] = clean
                    f.write(','.join(tokens))
                else:
                    f.write(line)
    if not os.path.isfile(paper_author_fn):
        done = {}
        print "Generating Author_refined.csv and PaperAuthor_refined.csv"
        with open("data/PaperAuthor.csv") as pa_file:
            f = open(paper_author_fn, 'w')
            for line in pa_file:
                tokens = line.split(',')
                if len(tokens) > 2:
                    if tokens[2] in done:
                        tokens[2] = done[tokens[2]]
                    else:
                        clean = remove_noise(tokens[2])
                        done[tokens[2]] = clean
                        tokens[2] = clean
                    f.write(','.join(tokens))
                else:
                    f.write(line)

def recover_all_author_names():
    author_fn = 'data/Author_refined_final.csv'
    paper_author_fn = 'data/PaperAuthor_refined_final.csv'

    token_dict, full_name_dict = load_refined_token_freq()

    if not os.path.isfile(author_fn):
        done = {}
        print "Generating Final version of Author_refined.csv"
        with open("data/Author_refined_simple.csv") as author_file:
            f = open(author_fn, 'w')
            for line in author_file:
                tokens = line.split(',')
                if len(tokens) > 1 and '?' in tokens[1]:
                    ori = tokens[1] 
                    if ori in done:
                        to = done[ori]
                    else:
                        to = recover_name(ori, token_dict, full_name_dict)
                        done[ori] = to
                    print ori, " -> ", to
                    tokens[1] = to
                    f.write(','.join(tokens))
                else:
                    f.write(line)
    else:
        print "Final version of Author_refined.csv is done"

    if not os.path.isfile(paper_author_fn):
        done = {}
        free_count = 10000
        i=0
        print "Generating Final version of Author_refined.csv and PaperAuthor_refined.csv"
        with open("data/PaperAuthor_refined_simple.csv") as pa_file:
            f = open(paper_author_fn, 'w')
            for line in pa_file:
                tokens = line.split(',')
                if len(tokens) > 2 and '?' in tokens[2]:
                    ori = tokens[2] 
                    if ori in done:
                        to = done[ori]
                    else:
                        to = recover_name(ori, token_dict, full_name_dict)
                        done[ori] = to
                    print ori, " -> ", to
                    tokens[2] = to
                    f.write(','.join(tokens))
                else:
                    f.write(line)
                if i < free_count:
                    i += 1
                else:
                    i = 0
                    gc.collect()
                    print "free memory"
    else:
        print "Final version of PaperAuthor_refined.csv is done"

def __fill_in_missing(name, i):
    res = []
    # remove '?'
    res.append(name[:i]+name[i+1:])
    # fill a english char in '?' position
    for l in string.lowercase:
        new_name = name[:i] + l + name[i+1:]
        res.append(new_name)
    return res

def __gen_all_possible_tokens(name):
    # locate invalid char position
    idxs = []
    for c in range(len(name)):
        if name[c] == '?':
            idxs.append(c)
    if len(idxs) > 0:
        if len(idxs) > 5:
            print name, " -- name contains too many missing"
        else:
            incomplete_names = __fill_in_missing(name, idxs[0])
            for i in range(1, len(idxs)):
                new_inames = []
                for iname in incomplete_names:
                    if idxs[i] < len(iname) - 1 and iname[idxs[i]] == '?' and len(iname) == len(name):
                        new_inames.extend(__fill_in_missing(iname, idxs[i]))
                    else:
                        new_inames.extend(__fill_in_missing(iname, idxs[i]-1))
                incomplete_names = new_inames
            incomplete_names.append(name.replace('?',''))
            return incomplete_names 
    return []

def recover_token(tokens, i, token_dict, full_name_dict):
    print "   *** recover_token: " + tokens[i]
    candidates = []
    possible_tokens = set(__gen_all_possible_tokens(tokens[i]))
#   print 'Jaaskelainen' in possible_tokens
#   print len(validate_set), 'jaaskelainen' in validate_set
    for ptoken in possible_tokens:
        if '?' not in ptoken and ptoken.lower() in token_dict:
            candidates.append((ptoken, token_dict[ptoken.lower()]))
    #print 'makila' in possible_tokens
    #print 'frederic' in possible_tokens
    if len(candidates) > 1:
        # try all candidates and see if it matches on the whole names
        res = []
        for c in candidates:
            tokens[i] = c[0]
            candidate_full_name = ' '.join(tokens)
            if candidate_full_name.lower() in full_name_dict:
                res.append((c[0], full_name_dict[candidate_full_name.lower()]))
        if len(res) > 0 and res[0][1] > 2:
            res = sorted(res, key=itemgetter(1), reverse=True)  
            print "   *** recovered_fu: ", res[0][0]
            return res[0][0]
        else:
            candidates = sorted(candidates, key=itemgetter(1), reverse=True)    
            print "   *** recovered_ca: ", candidates[0][0]
            return candidates[0][0] 
    elif len(candidates) == 1:
        print "   *** recovered_1c: ", candidates[0][0]
        return candidates[0][0]
    else:
        print "   *** cannot recover"
        return tokens[i].replace('?', '') 

def recover_merged_token(token, token_dict):
    print "   *** recover_merged_token: " + token
    candidates = []
    possible_tokens = set(__gen_all_possible_tokens(token))
    for ptoken in possible_tokens:
        if ptoken.lower() in token_dict:
            candidates.append((ptoken, token_dict[ptoken.lower()]))
    if len(candidates) > 0:
        candidates = sorted(candidates, key=itemgetter(1), reverse=True)    
        print "   *** recovered", candidates[0][0]
        return candidates[0][0]
    else:
        print "   *** cannot recover"
        return ""

def is_all_q(tok):
    for i in tok:
        if i != '?':
            return False
    return True

def merge_tokens(tokens, q_pos, token_dict, full_name_dict):
    q_tok = tokens[q_pos]
    merge = ""
    if len(q_tok) < 5:

        pre_token_ends_with_period = False
        
        q_tok_pos = ""
        # tob ia? lei
        if q_pos > 0 and q_pos < len(tokens) - 1:
            q_tok_pos = "middle"
            if tokens[q_pos-1][-1] == '.':
                pre_token_ends_with_period = True
        
        # ?obia lei
        if q_pos == 0:
            q_tok_pos = "first"

        # tobias l?i
        if q_pos == len(tokens) - 1:
            q_tok_pos = "last"
            if tokens[q_pos-1][-1] == '.':
                pre_token_ends_with_period = True
    
        merge_dir = ""
        # ????
        if is_all_q(q_tok):
            if pre_token_ends_with_period:
                merge_dir = "no"
            else:
                merge_dir = "both"
        # tobia?
        elif q_tok.rindex('?') == len(q_tok) - 1:
            merge_dir = "right"
        # ?obias
        elif q_tok.index('?') == 0:
            merge_dir = "left"
        else:
            merge_dir = "no"

        # X ? X = XX    
        if merge_dir == "both" and q_tok_pos == "middle":
            merge = tokens[q_pos-1] + tokens[q_pos+1]   
            
        # X? X = XX
        if merge_dir == "right" and q_tok_pos == "middle":
            merge = q_tok[:-1] + tokens[q_pos+1]    

        print merge_dir, q_tok_pos
        if merge:
            if merge.lower() in token_dict:
                tokens[q_pos] = merge
                if merge_dir == "both" and q_tok_pos == "middle":
                    tokens[q_pos-1] = ""
                    tokens[q_pos+1] = ""
                elif merge_dir == "right" and q_tok_pos == "middle":
                    tokens[q_pos+1] = ""        
            else:
                if merge_dir == "both" and q_tok_pos == "middle":
                    merge = tokens[q_pos-1] +'?'+ tokens[q_pos+1]   
                    res = recover_merged_token(merge, token_dict)
                    if res:
                        tokens[q_pos] = res
                        tokens[q_pos-1] = ""
                        tokens[q_pos+1] = ""
                    else:
                        # TODO
                        tokens[q_pos] = tokens[q_pos].replace('?','')   

                elif merge_dir == "right" and q_tok_pos == "middle":
                    merge = q_tok + tokens[q_pos+1] 
                    res = recover_merged_token(merge, token_dict)
                    if res:
                        tokens[q_pos] = res
                        tokens[q_pos+1] = ""
                    else:
                        # TODO
                        tokens[q_pos] = tokens[q_pos].replace('?','')   
            if q_tok_pos == "first":
                tokens[q_pos] = recover_token(tokens, q_pos, token_dict, full_name_dict)    
            if merge_dir == "no" and pre_token_ends_with_period:
                tokens[q_pos] = ""
        else:
            if len(tokens[q_pos]) == 1:
                tokens[q_pos] = tokens[q_pos].replace('?','')   
            else:
                tokens[q_pos] = recover_token(tokens, q_pos, token_dict, full_name_dict)    
        # remove empty tokens
        tokens = filter(None, tokens)
    else:
        # TODO: split Manuel e?lvarez -> Manuel e lvarez
        tokens[q_pos] = recover_token(tokens, q_pos, token_dict, full_name_dict)    

def get_candidates(token, token_dict):
    candidates = set() 
    possible_tokens = set(__gen_all_possible_tokens(token))
    for ptoken in possible_tokens:
        if ptoken.lower() in token_dict:
            candidates.add(ptoken)
    return candidates

def combine_candidates(tokens, candidates, token_dict, full_name_dict):
    print "   *** combine candidates, ", tokens
    #print candidates
    # remove all ? token
    for i in range(len(tokens)):
        if is_all_q(tokens[i]):
            tokens[i] = ""

    still_contain_q = False 
    for i in range(len(tokens)):
        if '?' in tokens[i]:
            still_contain_q = True
            break

    tokens = filter(None, tokens)
    if not still_contain_q:
        return ' '.join(tokens) 
            
    all_name_seq = []
    for c in candidates[tokens[0]]:
        all_name_seq.append([c])
    for i in range(1, len(tokens)):
        cur_name_seq = []
        for name_seq in all_name_seq:
            for c in candidates[tokens[i]]:
                new_name_seq = list(name_seq)
                new_name_seq.append(c)
                cur_name_seq.append(new_name_seq)
        all_name_seq = cur_name_seq
    # TODO: permutation and Tobias Lei -> T Lei, Tobias L etc
        
    final_candidates = []
    for name_seq in all_name_seq:
        name = ' '.join(name_seq)
        if name.lower() in full_name_dict:
            final_candidates.append((name, full_name_dict[name.lower()]))
    if final_candidates:
        final_candidates = sorted(final_candidates, key=itemgetter(1), reverse=True)    
        return final_candidates[0][0]
    else:
        print "   *** No Combination Found"
        name = ' '.join(tokens)
        name = name.replace('?', '')
        return name 

def recover_name(src_name, token_dict, full_name_dict):
    #tokens = re.split('[ -]', name)
    tokens = re.split('[ ]', src_name)
    q_pos = []
    for i in range(len(tokens)):
        if '?' in tokens[i]:
            q_pos.append(i)
    if len(q_pos) == 1:
        merge_tokens(tokens, q_pos[0], token_dict, full_name_dict)
        tokens = filter(None, tokens)
        return ' '.join(tokens).title()
    else:
        candidates = {}
        for t in tokens:
            if '?' in t:
                if len(t) > 2:
                    candidates[t] = get_candidates(t, token_dict)   
                    if not candidates[t]:
                        candidates[t] = set([t.replace('?', '')])
                else:
                    candidates[t] = set([t.replace('?','')])
            else:
                
                candidates[t] = set([t])
        return combine_candidates(tokens, candidates, token_dict, full_name_dict).title() 

recover_all_author_names()
