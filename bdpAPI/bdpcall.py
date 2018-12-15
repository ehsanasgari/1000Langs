import sys

import pandas as pd

sys.path.append('../')
from utility.file_utility import FileUtility
import requests
import codecs
import json
from multiprocessing import Pool
import tqdm
import collections
from pandas import Series


class BDPCall(object):

    def __init__(self, key, output_path, meta_file='../meta/meta.tsv'):

        # set the parameters
        self.key = key
        self.output_path = output_path
        self.meta_file = meta_file
        FileUtility.ensure_dir(self.output_path)
        FileUtility.ensure_dir(self.output_path + '/reports/')

        # check the API connection
        response = requests.get('https://dbt.io/api/apiversion?key=' + self.key + '&v=2')
        if response.status_code != 200:
            print('Enter you API code in the config file')
            return False
        else:
            response = json.loads(response.content)
            print('Connected successfully to bible digital platform v ' + response['Version'])
            self.load_book_map()

    def create_BPC(self, update_meta_data=True):
        self.df_all = pd.read_table(self.meta_file)
        if update_meta_data:
            self.update_meta_data()
        self.iso_dict = Series(self.df_all['ISO'].values, index=self.df_all['FCBH/DBS']).to_dict()

        self.df_exist = self.df_all[self.df_all['exist_API']].copy()
        self.df_exist['verses'] = 0
        # Crawl all bibles
        bible_length_map = self.crawl_bible_books()
        # Update the length column
        self.df_exist['verses'] = self.df_exist['FCBH/DBS'].map(lambda x: bible_length_map[x])
        self.df_exist.set_index('FCBH/DBS')
        self.df_exist.to_csv(self.output_path + '/reports/crawl_report.tsv', sep='\t')

    def load_book_map(self):
        self.book_map = dict()
        for l in FileUtility.load_list('../meta/books2numbers.txt'):
            for y in l.split('\t')[1].split(','):
                self.book_map[y] = l.split('\t')[0]

    def update_meta_data(self, nump=20):
        IDS = self.df_all['FCBH/DBS'].tolist()
        IDS.sort()
        existOnAPI = self.doesExist_bibleIDS(IDS, nump)
        self.df_all['exist_API'] = self.df_all['FCBH/DBS'].map(lambda x: existOnAPI[x])
        self.df_all.to_csv(self.meta_file, sep='\t')

    def crawl_bible_books(self, num_p=10):
        '''
        :param book_files_dir: this function needs to be called after doesExist_bibleIDS and this parameter is the same as output_path
        :param num_p:
        :return:
        '''
        book_meta_files = FileUtility.recursive_glob(self.output_path + '/bibles_metadata_api/', '*books.txt')
        res = BDPCall.make_parallel(num_p, self.crawl_a_book, book_meta_files)
        return res

    def crawl_a_book(self, bookmetafile):
        try:
            bible = dict()
            code = bookmetafile.split('/')[-1].split('_')[0]
            json_data = json.loads(codecs.open(bookmetafile, 'r', 'utf-8').read())
            dam_ids = set()
            for x in json_data:
                dam_ids.add(x['dam_id'])
            for x in dam_ids:
                response = requests.get('http://dbt.io/library/verse?key=' + self.key + '&dam_id=' + x + '2ET&v=2')
                book = json.loads(response.content.decode("utf-8"))
                for rec in book:
                    bible[self.book_map[rec['book_id']] + rec['chapter_id'].zfill(3) + rec['verse_id'].zfill(3)] = rec[
                        'verse_text'].strip()

            ordered_bible = collections.OrderedDict(sorted(bible.items()))
            bible = ['\t'.join([k, v]) for k, v in ordered_bible.items()]
            if len(bible)>0:
                FileUtility.save_list(self.output_path + '/' + '_'.join([self.iso_dict[code], code]) + '.txt', bible)

            return code, len(bible)
        except:
            return code, len(bible)

    def doesExist_bibleIDS(self, trlist, num_p):
        '''
        :param output_path: output directory
        :param trlist: translation list
        :param num_p: number of cores
        :return: boolean result on trlist
        '''
        FileUtility.ensure_dir(self.output_path + '/bibles_metadata_api/')
        res = BDPCall.make_parallel(num_p, self.doesExist_book, trlist)
        return res

    def doesExist_book(self, code):
        '''
        sub function
        :param code: 6 letter code of translation
        :return:
        '''
        response = requests.get('http://dbt.io/library/book?key=' + self.key + '&dam_id=' + code + '&v=2')
        res = False
        if (response.status_code == 200) and not response.content == b'[]':
            res = True
            F = codecs.open(self.output_path + '/bibles_metadata_api/' + code + '_books.txt', 'w', 'utf-8')
            F.write(response.content.decode("utf-8"))
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
    BDP_obj = BDPCall('f03a423aad95120f8eb40005070f19e9',
                      '/mounts/data/proj/asgari/final_proj/000_datasets/testbib/API')
    BDP_obj.create_BPC()
