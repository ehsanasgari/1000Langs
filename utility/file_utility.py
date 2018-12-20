__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__website__ = "https://llp.berkeley.edu/asgari/"
__git__ = "https://github.com/ehsanasgari/"
__email__ = "ehsan.asgari@gmail.com"
__project__ = "1000Langs -- Super parallel project at CIS LMU"

import sys
sys.path.append('../')

import _pickle as pickle
import codecs
import fnmatch
import os
from multiprocessing import Pool
import numpy as np
import tqdm
from scipy import sparse
import shutil


class FileUtility(object):
    def __init__(self):
        print('File utility object created..')


    @staticmethod
    def save_obj(filename, value):
        with open(filename + '.pickle', 'wb') as f:
            pickle.dump(value, f)

    @staticmethod
    def load_obj(filename):
        return pickle.load(open(filename, "rb"))

    @staticmethod
    def ensure_dir(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def exists(file_path):
        return os.path.exists(file_path)

    @staticmethod
    def remove(file_path):
        os.remove(file_path)


    @staticmethod
    def remove_dir(file_path):
        shutil.rmtree(file_path)

    @staticmethod
    def save_list(filename, list_names):
        #FileUtility.ensure_dir(filename)
        f = codecs.open(filename, 'w', 'utf-8')
        for x in list_names:
            f.write(x + '\n')
        f.close()

    @staticmethod
    def load_list(filename):
        return [line.strip() for line in codecs.open(filename, 'r', 'utf-8').readlines()]

    @staticmethod
    def save_sparse_csr(filename, array):
        np.savez(filename, data=array.data, indices=array.indices,
                 indptr=array.indptr, shape=array.shape)

    @staticmethod
    def load_sparse_csr(filename):
        loader = np.load(filename)
        return sparse.csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape'])

    @staticmethod
    def _float_or_zero(value):
        try:
            return float(value)
        except:
            return 0.0

    @staticmethod
    def recursive_glob(treeroot, pattern):
        '''
        :param treeroot: the path to the directory
        :param pattern:  the pattern of files
        :return:
        '''
        results = []
        for base, dirs, files in os.walk(treeroot):
            good_files = fnmatch.filter(files, pattern)
            results.extend(os.path.join(base, f) for f in good_files)
        return results
