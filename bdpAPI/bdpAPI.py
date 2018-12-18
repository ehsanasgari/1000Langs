__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__website__ = "https://llp.berkeley.edu/asgari/"
__git__ = "https://github.com/ehsanasgari/"
__email__ = "ehsan.asgari@gmail.com"
__project__ = "1000Langs -- Super parallel project at CIS LMU"

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


class BDPAPl(object):
    '''
        PBC retrieving from the bible digital platform
    '''
    def __init__(self, key, output_path):
        '''
            Constructor
        '''
        # set the parameters
        self.key = key
        self.output_path = output_path
        FileUtility.ensure_dir(self.output_path + '/api_intermediate/')
        FileUtility.ensure_dir(self.output_path + '/reports/')
        self.to_double_check=list()
        # check the API connection
        response = requests.get('https://dbt.io/api/apiversion?key=' + self.key + '&v=2')
        if response.status_code != 200:
            print('Enter you API code in the config file')
            return False
        else:
            response = json.loads(response.content)
            print('Connected successfully to bible digital platform v ' + response['Version'])
            self.load_book_map()

    def create_BPC(self, nump=20,update_meta_data=False, override=False, repeat=4):
        '''
            Creating PBC
        '''
        # update metadata file through api call
        if update_meta_data:
            self.update_meta_data()

        # read the metadata file and create the dataframe
        for line in codecs.open('../meta/api_volumes.txt','r','utf-8'):
            books=json.loads(line)
        books_filtered=([x for x in books if x['media']=='text'])
        df=pd.DataFrame(books_filtered)
        df['version'] = df[['version_code','volume_name']].apply(lambda x: ' # '.join(x), axis=1)
        df['trans_ID']=df['fcbh_id'].str[0:6]
        self.df=df[['language_iso','trans_ID','fcbh_id','language_english','language_name','version']]

        # bible retrieval
        self.id2iso_dict = Series(self.df['language_iso'].values, index=self.df['trans_ID']).to_dict()
        self.id2langeng_dict = Series(self.df['language_english'].values, index=self.df['trans_ID']).to_dict()
        self.id2lang_dict = Series(self.df['language_name'].values, index=self.df['trans_ID']).to_dict()
        self.id2version = Series(self.df['version'].values, index=self.df['trans_ID']).to_dict()

        # report creation
        report={'language_iso':[],'trans_ID':[],'language_english':[],'language_name':[],'version':[],'verses':[]}


        
        # retrieve all bibles
        bible_ids = self.ret_bible_books(nump=20,override=override)
        bible_ids = list(bible_ids.keys())
        bible_ids.sort()
        
        # iterating for max coverage
        continue_iter = True
        prev_missings = []
        missing_tr_list = []
        count=0
        while continue_iter and count < repeat:
            prev_missings = missing_tr_list
            missing_tr_list = []
            for trID in bible_ids:
                iso = self.id2iso_dict[trID]
                if not FileUtility.exists(self.output_path+'/'+iso+'_'+trID+'.api.txt'):
                    length=0
                    missing_tr_list.append(trID)
                else:
                    length=len(FileUtility.load_list(self.output_path+'/'+iso+'_'+trID+'.api.txt'))
                    report['language_iso'].append(iso)
                    report['trans_ID'].append(trID)
                    report['language_english'].append(self.id2langeng_dict[trID])
                    report['language_name'].append(self.id2lang_dict[trID])
                    report['version'].append(self.id2version[trID])
                    report['verses'].append(length)
            print ('Double checking of the missing translations..')
            bible_ids_new = self.ret_bible_books(nump=20,trList = missing_tr_list)
            bible_ids_new = list(bible_ids_new.keys())
            bible_ids_new.sort()
            count+=1;
            if missing_tr_list == prev_missings:
                continue_iter=False



        report=pd.DataFrame(report)
        report.set_index('trans_ID')
        report.to_csv(self.output_path + '/reports/crawl_report_API.tsv', sep='\t', index=False, columns=['language_iso','trans_ID','language_english','language_name','version','verses'])
        self.generate_final_rep()

    def load_book_map(self):
        '''
            loading book number mapping
        '''
        self.book_map = dict()
        for l in FileUtility.load_list('../meta/books2numbers.txt'):
            for y in l.split('\t')[1].split(','):
                self.book_map[y] = l.split('\t')[0]

    def update_meta_data(self):
        '''
            api call for updating the metadata file
        '''
        print ('Update API language file')
        response = requests.get('https://dbt.io/library/volume?key=' + self.key + '&v=2')
        if (response.status_code == 200):
            F = codecs.open('../meta/api_volumes.txt', 'w', 'utf-8')
            F.write(response.content.decode("utf-8"))
        F.close()

    def ret_bible_books(self, nump=10, trList=[], override=False):
        '''
        Retrieving all bibles
        :param nump:
        :return:
        '''
        
        # parallel input creation
        tr_meta=[]
        exists=dict()
        for x in (self.df['trans_ID'].unique().tolist() if len(trList)==0 else trList):
            
            if not FileUtility.exists(self.output_path+'/'+self.id2iso_dict[x]+'_'+x+'.api.txt') or override:
                tr_meta.append((self.df[self.df['trans_ID']==x]['language_iso'].tolist()[0],x,self.df[self.df['trans_ID'] ==x]['fcbh_id'].tolist()))
            else:
                exists[x]='existed'
                
            
        # call in parallel
        print('Retrieving the bible translation')
        res = BDPAPl.make_parallel(min(nump,len(tr_meta)), self.ret_a_book, tr_meta)
        res.update(exists)
        
        return res

    def ret_a_book(self, tr_meta):
        
        isocode, trID, dam_ids=tr_meta
        
        # store the api call results in json
        file_path=self.output_path + '/api_intermediate/'+'_'.join([isocode,trID])+'.json'
        f=codecs.open(file_path, 'w', 'utf-8')
        for x in dam_ids:
            response = requests.get('http://dbt.io/library/verse?key=' + self.key + '&dam_id=' + x + '&v=2')
            f.write(response.content.decode("utf-8")+'\n')
        f.close()
        
        # read the books
        books = []
        for line in codecs.open(file_path,'r','utf-8'):
            try:
                books.append(json.loads(line))
            except:
                self.to_double_check.append(tr_meta)
                
        # parse the books
        bible = dict()
        for book in books:
            for rec in book:
                bible[self.book_map[rec['book_id']] + rec['chapter_id'].zfill(3) + rec['verse_id'].zfill(3)] = rec[
                    'verse_text'].strip()

        # save the books
        ordered_bible = collections.OrderedDict(sorted(bible.items()))
        bible = ['\t'.join([k, v]) for k, v in ordered_bible.items()]
        if len(bible)>0:
            FileUtility.save_list(self.output_path + '/' + '_'.join([isocode,trID]) + '.api.txt', bible)
       
        return trID, len(bible)

    @staticmethod
    def make_parallel(nump, func, in_list):
        pool = Pool(processes=nump)
        final_res = dict()
        for idx, res in tqdm.tqdm(pool.imap_unordered(func, in_list, chunksize=nump), total=len(in_list)):
            final_res[idx] = res
        pool.close()
        return final_res
    
    def generate_final_rep(self):
        rep_files=FileUtility.recursive_glob(self.output_path+'/reports/','crawl_report_*.tsv')
        df_s=[]
        for report_file in rep_files:
            version=report_file.split('/')[-1].split('.')[0].split('_')[-1]
            temp=pd.read_table(report_file)[['trans_ID','language_iso','language_name','verses']]
            temp['source']=version
            df_s.append(temp.copy())
        df_s=pd.concat(df_s)
        df_s.set_index('trans_ID')
        self.aggregated_rep=df_s
        df_s.to_csv(self.output_path + '/reports/final_rep.tsv', sep='\t', index=False, columns=['language_iso','trans_ID','language_name','verses','source'])



if __name__ == '__main__':
    BDP_obj = BDPAPl('f03a423aad95120f8eb40005070f19e9',
                      '/mounts/data/proj/asgari/final_proj/000_datasets/testbib/API')
    BDP_obj.create_BPC()
    

