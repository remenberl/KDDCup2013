#-*- coding: UTF-8 -*-
import cPickle
import os
from custom_setting import *
import difflib
import re
import string
import unicodedata

def remove_noise_simple(src_name):
    name = src_name.decode('utf-8')
    return unicodedata.normalize('NFKD', name).encode('ascii','ignore')

def remove_noise(src):
    src = src.decode('utf-8')

    pattern = re.compile(u'è\·ˉ |È\·ˉ |è\·ˉ|È\·ˉ', re.MULTILINE)
    s = pattern.sub('', src)

    pattern = re.compile(u'@.*|[? ]author.email:.*', re.MULTILINE)
    s = pattern.sub('', s)

    s = s.replace(r'\xi', '')
    s = s.replace(r'\phi', '')
    s = s.replace(r'\delta', '')
    s = s.replace(u'é', 'e')
    s = s.replace(u'ó', 'o')

    pattern = re.compile(u'[àáâãäåæ]|(¨¢)+', re.MULTILINE)
    s = pattern.sub('a', s)

    pattern = re.compile(u'[ÀÁÂÃÄÅÆ]', re.MULTILINE)
    s = pattern.sub('A', s)

    pattern = re.compile(u'[èéêëȩ]|¨\||¨¨|¨e|¨¦', re.MULTILINE)
    s = pattern.sub('e', s)

    pattern = re.compile(u'[ÈÉÊË]', re.MULTILINE)
    s = pattern.sub('E', s)

    pattern = re.compile(u' ı', re.MULTILINE)
    s = pattern.sub('i', s)

    pattern = re.compile(u'[ìíîïı]|¨a|¨ª', re.MULTILINE)
    s = pattern.sub('i', s)

    pattern = re.compile(u'[ÌÍÎÏ]', re.MULTILINE)
    s = pattern.sub('I', s)

    pattern = re.compile(u'[ðđ]', re.MULTILINE)
    s = pattern.sub('d', s)

    pattern = re.compile(u'[ÐĐ]', re.MULTILINE)
    s = pattern.sub('D', s)

    pattern = re.compile(u'[ñ]', re.MULTILINE)
    s = pattern.sub('n', s)

    pattern = re.compile(u'[Ñ]', re.MULTILINE)
    s = pattern.sub('N', s)

    pattern = re.compile(u'[òóôõöø]|¨°|¨®|¨o', re.MULTILINE)
    s = pattern.sub('o', s)

    pattern = re.compile(u'[ÒÓÔÕÖØ]', re.MULTILINE)
    s = pattern.sub('O', s)

    pattern = re.compile(u'[ùúûü]|¨²|¨¹|¨u', re.MULTILINE)
    s = pattern.sub('u', s)

    pattern = re.compile(u'[ÙÚÛÜ]', re.MULTILINE)
    s = pattern.sub('U', s)

    pattern = re.compile(u'[Ýýÿ]', re.MULTILINE)
    s = pattern.sub('y', s)

    pattern = re.compile(u'[Ý]', re.MULTILINE)
    s = pattern.sub('Y', s)

    pattern = re.compile(u'[Þþ]', re.MULTILINE)
    s = pattern.sub('p', s)

    pattern = re.compile(u'[çčć]', re.MULTILINE)
    s = pattern.sub('c', s)

    pattern = re.compile(u'[Ç]', re.MULTILINE)
    s = pattern.sub('C', s)

    pattern = re.compile(u'¨f', re.MULTILINE)
    s = pattern.sub('ef', s)

    pattern = re.compile(u'[łŁ]|¨l', re.MULTILINE)
    s = pattern.sub('l', s)

    pattern = re.compile(u'Ł', re.MULTILINE)
    s = pattern.sub('L', s)

    pattern = re.compile(u'ž', re.MULTILINE)
    s = pattern.sub('z', s)

    pattern = re.compile(u'Ž', re.MULTILINE)
    s = pattern.sub('Z', s)

    pattern = re.compile(u'š', re.MULTILINE)
    s = pattern.sub('s', s)

    pattern = re.compile(u'ß', re.MULTILINE)
    s = pattern.sub('b', s)

    pattern = re.compile(u' ¨\.', re.MULTILINE)
    s = pattern.sub('.', s)

    pattern = re.compile(u' º | ¨ |¨ |° |° | ¨ |¨ | ¨| \?ˉ\? |\?ˉ\? |\?ˉ\?|ˉ\? |ˉ\?| ´ |´ | ´| ˝ |˝ | ˘ | ˜ | ˆ | ‰ |‰ | » |» ', re.MULTILINE)
    s = pattern.sub('', s)

    s = s.replace(u' ³ ', ' ')

    pattern = re.compile(u"[¯´ˉ’‘ˆ°¨¸³·»~«˘'""\\\\]", re.MULTILINE)
    s = pattern.sub('', s)

    pattern = re.compile(u"[  ]", re.MULTILINE)
    s = pattern.sub(' ', s)

    return unicodedata.normalize('NFKD', s).encode('ascii','ignore')

def generate_new_author_names():
    author_fn = 'data/Author_refined_simple.csv'
    paper_author_fn = 'data/PaperAuthor_refined_simple.csv'
    if not os.path.isfile(author_fn):
        done = {}
        print "Generating Author_refined, simple non-ascii to ascii"
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
        print "Generating PaperAuthor_refined, simple non-ascii to ascii"
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

generate_new_author_names()
