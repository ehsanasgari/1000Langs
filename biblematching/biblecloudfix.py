
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
    for bible in bible_files:
        if bible[0] in dict_bible:
            print(bible[1], dict_bible[bible[0]])
        else:
            print(bible[1])
