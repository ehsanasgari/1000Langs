
__author__ = "Ehsaneddin Asgari"

import sys
sys.path.append("../")

from parallelbible.accessbible import AccessBible
from utility.file_utility import FileUtility
import collections
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import string
import tqdm
from multiprocessing import Pool
import codecs
import re
import os


if __name__ == '__main__':
    bible_files=FileUtility.recursive_glob('/mounts/data/proj/asgari/final_proj/000_datasets/testbib/extracted_bibles/','*.txt')
    tr_file_dict={l.split()[0]:l.split()[1] for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/lang_urls.txt')}
    dict_url={l.split()[0]:l.split()[1] for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/finalized_urls/biblecloud.txt')}
    dict_url.update({l.split()[0]:l.split()[1] for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/finalized_urls/bibleis.txt')})
    dict_url.update({l.split()[0]:l.split()[1] for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/finalized_urls/pngscriptures.txt')})
    dict_url.update({l.split()[0]:l.split()[1] for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/handled_bible.com.txt')})
    sparse=[]
    for file in tqdm.tqdm(bible_files):
        res=[1 if l.split()[1:3]==['1','1'] else 0 for l in FileUtility.load_list(file)[1::] if l.split()[1:3]==['1','0'] or l.split()[1:3]==['1','1']]
        if np.mean(res) ==0:
            sparse.append('\t'.join([dict_url[file.split('/')[-1]],file.split('/')[-1],str(round(np.mean(res),2))]))
    sparse.sort()
    FileUtility.save_list('sparse_translations.txt',sparse)
