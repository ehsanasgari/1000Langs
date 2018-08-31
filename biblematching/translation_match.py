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
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import string

if __name__ == '__main__':

    AccBible = AccessBible(AccessBible.path)

    translate_table = dict((ord(char), None) for char in string.punctuation)
    michael = collections.OrderedDict(AccBible.get_subcorpus_bible_by_lang_trans_filtered('acd','bible'))
    crawled = collections.OrderedDict(dict([(l.split()[0], ' '.join(l.split()[1::])) for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/000_datasets/testbib/bibleis/acd-x-bible.txt')]))
    print(len(michael),len(crawled),len(set(michael).intersection(crawled)))

    michael_verses=[l.replace(' ','').translate(translate_table) for l in list(michael.values())]
    crawled_verses=[l.replace(' ','').translate(translate_table) for l in list(crawled.values())]

    michael_keys=list(michael.keys())
    crawled_keys=list(crawled.keys())

    all=michael_verses+crawled_verses

    tp=TfidfVectorizer(use_idf=False, analyzer='char', ngram_range=(1,3), norm='l2', stop_words=[], lowercase=False, binary=False)
    X=tp.fit_transform(all).toarray()
    X_michl=X[0:len(michael_verses),:]
    X_crawl=X[len(michael_verses):,:]
    sim=X_michl.dot(X_crawl.T)

    most_sim_to_crawl_in_michael=np.argmax(sim, axis=0)
    most_sim_to_michael_in_crawl=np.argmax(sim, axis=1)

    mismatches=[]
    mapping_crawl2michael=dict()

    for idx, michael_key in enumerate(michael_keys):
        found_in_crawl=crawled_keys[most_sim_to_michael_in_crawl[idx]]
        crawl_key_idx=crawled_keys.index(michael_key)
        if sim[idx,crawl_key_idx]>0.9:
            mapping_crawl2michael[michael_key]=crawled_keys[crawl_key_idx]
        elif not found_in_crawl == michael_key and sim[idx,most_sim_to_michael_in_crawl[idx]]>0.9:
            mapping_crawl2michael[michael_key]=found_in_crawl
        else:
            mismatches.append(michael_key)
            print (sim[idx,crawled_keys.index(michael_key)])
            print (michael_key, michael_verses[idx], '=========')
            print (michael_key, crawled_verses[most_sim_to_michael_in_crawl[idx]])
            print (crawled_keys[most_sim_to_michael_in_crawl[idx]], crawled_verses[most_sim_to_michael_in_crawl[idx]])

