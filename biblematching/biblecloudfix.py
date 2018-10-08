
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
    bible_files=[(x.split()[1][0:3],x.split()[1]) for x in FileUtility.load_list('temp.txt')]
    dict_bible={l.split()[0]:l.split()[1] for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/superpivot/wals/wals_data/ISO639-3.tsv')}
    dict_url={l.split()[0]:l.split()[1] for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/handled_pngscriptures.org.txt')}
    file_content=[]
    for bible in bible_files:
        file_content.append(' '.join([bible[1],dict_url[bible[1]]]))
        if bible[0] in dict_bible:
            print(bible[1], dict_bible[bible[0]])
        else:
            print(bible[1])
    FileUtility.save_list('/mounts/data/proj/asgari/final_proj/1000langs/config/pngscriptures_remained.txt',file_content)

# import sys
# sys.path.append("../")
# from utility.file_utility import FileUtility
# bc1=dict([tuple(x.split()) for x in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/handled_pngscriptures.org.txt')])
# bc1.update(dict([tuple(x.split()) for x in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/pngscriptures_remained.txt')]))
# langs=list(bc1.keys())
# langs.sort()
# final_bc=[' '.join([l, bc1[l]]) for l in langs]
# FileUtility.save_list('/mounts/data/proj/asgari/final_proj/1000langs/config/finalized_urls/pngscriptures.txt',final_bc)
