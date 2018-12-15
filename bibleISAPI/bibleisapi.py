import sys
sys.path.append('../')
from utility.file_utility import FileUtility
import requests
import codecs
import json
from multiprocessing import Pool
import tqdm
import collections
import pandas as pd
from pandas import Series


class BibleISAPI(object):
    '''
        BibleIS.com
    '''
    def __init__(self, output_path, meta_file='../meta/meta.tsv'):
        # set the parameters
        self.output_path = output_path
        self.meta_file = meta_file
        FileUtility.ensure_dir(self.output_path)
        FileUtility.ensure_dir(self.output_path + '/reports/')


    def update_meta_data(self, nump=20):
        df1=pd.read_table('../meta/meta.tsv')
        df2=pd.read_table('/mounts/data/proj/asgari/final_proj/000_datasets/testbib/API/reports/crawl_report_API.tsv')
        IDS=set(df2[df2['verses']==0]['FCBH/DBS'].tolist()+df1[df1['exist_API']==False]['FCBH/DBS'].tolist())
        existOnAPI = self.doesExist_bibleIDS(IDS, nump)
        self.df_all['exist_BibleIS'] = 0
        self.df_all['exist_BibleIS'] = self.df_all['FCBH/DBS'].map(lambda x: existOnAPI[x])
        self.df_all.to_csv(self.meta_file, sep='\t')

    def doesExist_bibleIDS(self, trlist, num_p):
        '''
        :param output_path: output directory
        :param trlist: translation list
        :param num_p: number of cores
        :return: boolean result on trlist
        '''
        FileUtility.ensure_dir(self.output_path + '/bibles_metadata_bibleis/')
        res = BibleISAPI.make_parallel(num_p, self.doesExist_book, trlist)
        return res

    def doesExist_book(self, code):
        '''
        sub function
        :param code: 6 letter code of translation
        :return:
        '''
        response = requests.get('http://www.bible.is/'+code+'/Matt/1')
        res = False
        if (response.status_code == 200):
            res = True
        return code, res

    @staticmethod
    def make_parallel(num_p, func, in_list):
        pool = Pool(processes=num_p)
        final_res = dict()
        for idx, res in tqdm.tqdm(pool.imap_unordered(func, in_list, chunksize=num_p), total=len(in_list)):
            final_res[idx] = res
        pool.close()
        return final_res


if __name__ == '__main__':
    BDP_obj = BibleISAPI('/mounts/data/proj/asgari/final_proj/000_datasets/testbib/API')
    BDP_obj.create_BPC()
