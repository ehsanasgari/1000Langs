#!/usr/bin/env python3
import sys

sys.path.append('../')
from utility.file_utility import FileUtility
import collections

if __name__ == '__main__':
    url_pattern = 'pngscriptures.org'
    language_dict = dict([tuple(l.split('\t')) for l in FileUtility.load_list('remained.txt')])
    extracted_dict = dict()
    remained_dict = dict()
    for x, y in language_dict.items():
        flag = False
        for z in y.split():
            if url_pattern in z:
                flag = True
                extracted_dict[x] = z
        if not flag:
            remained_dict[x] = y

    extracted_dict = collections.OrderedDict(extracted_dict)
    remained_dict = collections.OrderedDict(remained_dict)

    FileUtility.save_list('handled_' + url_pattern + '.txt', ['\t'.join([x, y]) for x, y in extracted_dict.items()])
    FileUtility.save_list('remained.txt', ['\t'.join([x, y]) for x, y in remained_dict.items()])
