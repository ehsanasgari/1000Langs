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
from Bio import SeqIO
from Bio.Alphabet import generic_dna
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from scipy import sparse
import h5py
import shutil


class FileUtility(object):
    def __init__(self):
        print('File utility object created..')

    @staticmethod
    def create_fasta_file(file_address, corpus, label):
        seq_id_pairs = [('.'.join([str(idx + 1), label[idx]]), x) for idx, x in enumerate(corpus)]
        seq_recs = [SeqRecord(Seq(seq, generic_dna), id=id, description='') for id, seq in seq_id_pairs]
        SeqIO.write(seq_recs, file_address, "fasta")


    @staticmethod
    def read_sequence_file(file_name_sample):
        '''
        :param file_name_sample:
        :return:
        '''
        corpus = []
        if file_name_sample[-1] == 'q':
            for cur_record in SeqIO.parse(file_name_sample, "fastq"):
                corpus.append(str(cur_record.seq).lower())
        else:
            for cur_record in SeqIO.parse(file_name_sample, "fasta"):
                corpus.append(str(cur_record.seq).lower())
        return file_name_sample.split('/')[-1], corpus

    @staticmethod
    def read_sequence_file_length(file_name_sample):
        '''
        :param file_name_sample:
        :return:
        '''
        corpus = []
        if file_name_sample[-1] == 'q':
            for cur_record in SeqIO.parse(file_name_sample, "fastq"):
                corpus.append(str(cur_record.seq).lower())
        else:
            for cur_record in SeqIO.parse(file_name_sample, "fasta"):
                corpus.append(str(cur_record.seq).lower())
        return file_name_sample.split('/')[-1], len(corpus)


    @staticmethod
    def read_fasta_directory(file_directory, file_extenstion, only_files=[]):
        '''
        :param file_directory:
        :param file_extenstion:
        :param only_files:
        :return: list of fasta files, and a dic to map file to index
        '''
        if len(only_files) > 0:
            fasta_files = [x for x in FileUtility.recursive_glob(file_directory, '*.' + file_extenstion) if
                           x.split('/')[-1] in only_files]
        else:
            fasta_files = [x for x in FileUtility.recursive_glob(file_directory, '*.' + file_extenstion)]

        fasta_files.sort()
        mapping = {v: k for k, v in enumerate(fasta_files)}
        return fasta_files, mapping


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

    @staticmethod
    def read_fasta_sequences(file_name):
        corpus=[]
        for cur_record in SeqIO.parse(file_name, "fasta"):
                corpus.append(str(cur_record.seq).lower())
        return corpus

    @staticmethod
    def read_fasta_sequences_ids(file_name):
        corpus=dict()
        for cur_record in SeqIO.parse(file_name, "fasta"):
                corpus[str(cur_record.id)]=(str(cur_record.seq).lower(),str(cur_record.description))
        return corpus


    @staticmethod
    def loadH5file(filename):
        f = h5py.File(filename, 'r')
        a_group_key = list(f.keys())[0]
        return list(f[a_group_key])
