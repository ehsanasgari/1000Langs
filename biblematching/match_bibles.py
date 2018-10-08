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

import difflib
import string

global translate_table
translate_table = dict((ord(char), None) for char in list(string.punctuation)+[' ','\t'])

def get_overlap(s1, s2):
    global translate_table
    s1=s1.translate(translate_table)
    s2=s2.translate(translate_table)
    s = difflib.SequenceMatcher(None, s1, s2)
    # to find overlap
    #pos_a, pos_b, size = s.find_longest_match(0, len(s1), 0, len(s2))
    #len(s1[pos_a:pos_a+size])/max(len(s1),len(s2))
    return s.quick_ratio()

def get_diff(bible_file):

    global AccBible

    trans=bible_file.split('/')[-1].split('.')[0].split('-')[-1].replace(' ', '')
    iso_name=bible_file.split('/')[-1].split('-')[0]


    try:
        michael = collections.OrderedDict(AccBible.get_subcorpus_bible_by_lang_trans_filtered(iso_name,trans))
    except:
        return bible_file, [], []

    try:
        crawled = collections.OrderedDict(dict([(l.split()[0], ' '.join(l.split()[1::])) for l in FileUtility.load_list(bible_file)]))
    except:
        crawled = collections.OrderedDict(dict())

    all_verseIDs=list(set(list(crawled.keys())+list(michael.keys())))
    all_verseIDs.sort()

    miss_matches=[]
    vecs=[['verseID','BPC','CRWL','Match','Verse']]
    for idx in all_verseIDs:
        if (idx in michael) and (idx not in crawled):
            vecs.append([idx, '1', '0', '0', '-'])
        if (idx not in michael) and (idx in crawled):
            if len(crawled[idx].strip())>0:
                vecs.append([idx, '0', '1', '1', crawled[idx]])
        if (idx in michael) and (idx in crawled):
            match_ratio= round(get_overlap(crawled[idx],michael[idx]),2)
            if match_ratio>0 and match_ratio<0.9:
                miss_matches.append('\t'.join([idx, bible_file,str(match_ratio)]))
            vecs.append([idx, '1', '1', str(match_ratio), crawled[idx]])

    translation=['\t'.join(vec) for vec in vecs]

    return bible_file, translation,miss_matches

if __name__ == '__main__':
    global AccBible
    AccBible = AccessBible(AccessBible.path)
    miss_matches=[]
    for website in ['pngscript']#['bibleis','biblecom','pngscript','biblecloud']:
        miss_matches+=[website+'---------------------------------------------']
        files=FileUtility.recursive_glob('/mounts/data/proj/asgari/final_proj/000_datasets/testbib/'+website+'/','*.txt')
        corrects=[]
        needs_fixing=[]

        pool = Pool(processes=10)
        for bible_file , translation,miss_match in tqdm.tqdm(pool.imap_unordered(get_diff, files, chunksize=10),total=len(files)):
            FileUtility.save_list('/mounts/data/proj/asgari/final_proj/000_datasets/testbib/extracted_bibles/'+bible_file.split('/')[-1],translation)
            miss_matches+=miss_match
    FileUtility.save_list('found.txt',miss_matches)
    pool.close()

