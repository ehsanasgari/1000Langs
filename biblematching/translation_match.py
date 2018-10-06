import codecs
import re
import os
import sys

__author__ = "Ehsaneddin Asgari"

sys.path.append("../")

import seaborn as sns; sns.set()
from parallelbible.accessbible import AccessBible
from utility.file_utility import FileUtility
import collections
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import string
import tqdm
from multiprocessing import Pool


'''
TODO:
consider empty verses
'''
#    all=michael_verses+crawled_verses
#    tp=TfidfVectorizer(use_idf=False, analyzer='char', ngram_range=(1,3), norm='l2', stop_words=[], lowercase=False, binary=False)
#    X=tp.fit_transform(all).toarray()
#    X_michl=X[0:len(michael_verses),:]
#    X_crawl=X[len(michael_verses):,:]
#    sim=X_michl.dot(X_crawl.T)

# if X_crawl.shape[0]>1:
#     most_sim_to_crawl_in_michael=np.argmax(sim, axis=0)
#     most_sim_to_michael_in_crawl=np.argmax(sim, axis=1)
#
#     mismatches=[]
#     mapping_michael2crawl=dict()
#
#     for idx, michael_key in enumerate(michael_keys):
#         found_in_crawl=crawled_keys[most_sim_to_michael_in_crawl[idx]]
#         if michael_key in crawled_keys:
#             crawl_key_idx=crawled_keys.index(michael_key)
#             if sim[idx,crawl_key_idx]>0.9:
#                 mapping_michael2crawl[michael_key]=crawled_keys[crawl_key_idx]
#         elif not found_in_crawl == michael_key and sim[idx,most_sim_to_michael_in_crawl[idx]]>0.95:
#             mapping_michael2crawl[michael_key]=found_in_crawl
#         else:
#             mismatches.append((michael_key,sim[idx,most_sim_to_michael_in_crawl[idx]]))
#             #print (sim[idx,crawled_keys.index(michael_key)])
#             #print (michael_key, michael_verses[idx], '=========')
#             #print (michael_key, crawled_verses[most_sim_to_michael_in_crawl[idx]])
#             #print (crawled_keys[most_sim_to_michael_in_crawl[idx]], crawled_verses[most_sim_to_michael_in_crawl[idx]])
#     return (bible_file, mapping_michael2crawl, mismatches, len(mapping_michael2crawl)/len(michael), iso_name, trans )
# return bible_file,{},[],0,iso_name,trans


def get_diff(bible_file):

    global AccBible

    trans=bible_file.split('/')[-1].split('.')[0].split('-')[-1].replace(' ', '')
    iso_name=bible_file.split('/')[-1].split('-')[0]

    translate_table = dict((ord(char), None) for char in string.punctuation)

    try:
        michael = collections.OrderedDict(AccBible.get_subcorpus_bible_by_lang_trans_filtered(iso_name,trans))
    except:
        print (bible_file)
        return bible_file, [], []

    try:
        crawled = collections.OrderedDict(dict([(l.split()[0], ' '.join(l.split()[1::])) for l in FileUtility.load_list(bible_file)]))
    except:
        crawled = collections.OrderedDict(dict())


    michael_verses=[l.replace(' ','').translate(translate_table) for l in list(michael.values())]
    crawled_verses=[l.replace(' ','').translate(translate_table) for l in list(crawled.values())]

    michael_keys=list(michael.keys())
    crawled_keys=list(crawled.keys())

    matches=[]
    missmatches=[]


    for idx, michael_key in enumerate(michael_keys):
        if michael_key in crawled_keys:
            crawl_key_idx=crawled_keys.index(michael_key)
            if michael_verses[idx]==crawled_verses[crawl_key_idx]:
                matches.append(michael_key)
            else:
                missmatches.append('\t'.join([michael_key,michael[michael_key]]))
        else:
            missmatches.append('\t'.join([michael_key,michael[michael_key]]))

    return bible_file, matches, missmatches

if __name__ == '__main__':
    global AccBible
    AccBible = AccessBible(AccessBible.path)
    files=FileUtility.recursive_glob('/mounts/data/proj/asgari/final_proj/000_datasets/testbib/biblecloud/','*.txt')
    corrects=[]
    needs_fixing=[]

    pool = Pool(processes=10)

    for bible_file ,match, missmatch in tqdm.tqdm(pool.imap_unordered(get_diff, files, chunksize=10),total=len(files)):
        FileUtility.save_list('/mounts/data/proj/asgari/final_proj/000_datasets/testbib/aggregate/match_'+bible_file.split('/')[-1],match)
        FileUtility.save_list('/mounts/data/proj/asgari/final_proj/000_datasets/testbib/aggregate/missmatch_'+bible_file.split('/')[-1],missmatch)
    pool.close()
