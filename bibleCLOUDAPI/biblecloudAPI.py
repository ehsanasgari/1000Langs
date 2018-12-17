__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__email__ = "asgari@berkeley.edu"
__project__ = "Super parallel project at CIS LMU"
__website__ = "https://llp.berkeley.edu/asgari/"

import sys
sys.path.append('../')
import numpy as np
import tqdm
import re
from multiprocessing import Pool
from biblecrawler.bibleCLOUD import BibleCloud
from pandas import Series
from utility.file_utility import FileUtility
import pandas as pd
import requests
from bs4 import BeautifulSoup
from metaAPI.metadata import getMetaMerged

class BibleCloudAPl(object):
    '''
        PBC retrieving from the bible cloud
    '''
    def __init__(self, output_path):
        '''
            Constructor
        '''
        # set the parameters
        self.output_path = output_path
        FileUtility.ensure_dir(self.output_path + '/biblecloud_intermediate/')
        FileUtility.ensure_dir(self.output_path + '/reports/')
        self.make_bible_cloud_list()

    def make_bible_cloud_list(self):
        # get all metadata available
        print ('Retrieving bible meta data from online resources..')
        self.df_meta=getMetaMerged()
        # prepare list of all potential languages
        print ('Preparing meta data and list of languages on bible cloud')
        self.get_all_languages_in_cloud()
        # get a final list of languages with meta data
        self.df_cloud=self.get_bible_cloud_new()
        # bible retrieval
        self.id2iso_dict = Series(self.df_cloud['language_iso'].values, index=self.df_cloud['trans_ID']).to_dict()
        self.id2lang_dict = Series(self.df_cloud['language_name'].values, index=self.df_cloud['trans_ID']).to_dict()
        self.id2version = Series(self.df_cloud['Description'].values, index=self.df_cloud['trans_ID']).to_dict()

    def get_all_languages_in_cloud(self):
        # get list of all languages
        base_url = 'https://bible.cloud/inscript/content/texts/'
        soup = BeautifulSoup(requests.get(base_url).content)
        self.mapping=dict()
        for link in tqdm.tqdm(soup.select('a')):
            if 'class' in link.attrs:
                if len(link.contents)==1:
                    if 'href' in link.attrs:
                        self.mapping[link.attrs['href'].split('/')[0]]=('https://bible.cloud/inscript/content/texts/'+link.attrs['href'].replace('index.html','MT1.html'),link.contents[0].replace(' ','-'))

    def get_bible_cloud_new(self, nump=20):

        # find languages does not exist in the api
        df_API=pd.read_table(self.output_path+'/reports/crawl_report_API.tsv')
        api_existing=df_API.trans_ID.tolist()
        new_translations=list(set(self.mapping)-set(api_existing))

        # find languages meta data from find bible
        cloud_with_meta=self.df_meta[self.df_meta['trans_ID'].isin(new_translations)]
        # find the one without meta data
        cloud_without=set(new_translations)-set(cloud_with_meta.trans_ID.tolist())
        # get the meta data from the bible cloud if available
        print ('Get the missing metadata from bible cloud..')
        res_dict = BibleCloudAPl.make_parallel(nump,BibleCloudAPl.get_cloud_record,cloud_without)

        # prepare the dataframe
        res=[]
        for x,y in res_dict.items():
            if y:
                res.append(y)
        df_cloud=pd.concat([cloud_with_meta,pd.DataFrame(res, columns=['language_iso', 'trans_ID','language_name','Year','Description'])])
        df_cloud=df_cloud[['trans_ID','language_iso','language_name','Description','Year']]
        df_cloud.set_index('trans_ID')
        return df_cloud

    @staticmethod
    def make_parallel(num_p, func, in_list):
        pool = Pool(processes=num_p)
        final_res = dict()
        for idx, res in tqdm.tqdm(pool.imap_unordered(func, in_list, chunksize=num_p), total=len(in_list)):
            final_res[idx] = res
        pool.close()
        return final_res

    @staticmethod
    def get_cloud_record(trCode):
        global df_metabib
        response = requests.get('https://bible.cloud/inscript/content/texts/'+trCode+'/about.html')
        if response.status_code == 200:
            soup = BeautifulSoup(requests.get('https://bible.cloud/inscript/content/texts/'+trCode+'/about.html').content)
            try:
                description=soup.select('h2')[0].text
            except:
                description=''
            try:
                iso=[x.attrs['href'].split('/')[-1] for x in soup.select('a[href]') if 'ethnologue.org/language/' in x.attrs['href']][-1]
            except:
                if trCode[0:3]=='SPN':
                    iso='spa'
                else:
                    iso='NotAvailable'
            try:
                lang=[x.text for x in soup.select('a[href]') if 'ethnologue.org/language/' in x.attrs['href']][-1]
            except:
                lang='Not available'
            try:
                year=[w for w in str(soup.select('p')[0]).split() if re.search('^[0-9]{4}$', w)][0]
            except:
                year=[w for w in soup.text.split() if re.search('^[0-9]{4}$', w)][0]
        else:
            return trCode, False
        return trCode,[iso, trCode, lang, year, description]

    def crawl_bible_cloud(self, nump=20, override=False):
        urls=('https://bible.cloud/inscript/content/texts/'+ self.df_cloud['trans_ID']+'/MT1.html').tolist()
        outputs=[self.output_path + '/biblecloud_intermediate/']*len(self.df_cloud['trans_ID'].tolist())
        txt_files=('../'+self.df_cloud['language_iso']+'_'+self.df_cloud['trans_ID']+'.cloud.txt').tolist()
        triples=[(url,outputs[idx],txt_files[idx]) for idx,url in enumerate(urls)]

        if not override:
            new_list=[]
            for x,y,z in triples:
                if not FileUtility.exists(y):
                    new_list.append((x,y,z))
            triples=new_list

        BibleCloud.parallel_crawl(triples, nump, True)
        self.create_report_cloud()

    def create_report_cloud(self):
        report={'language_iso':[],'trans_ID':[],'language_name':[],'Description':[],'verses':[]}
        for trID in self.df_cloud.trans_ID:
            iso = self.id2iso_dict[trID]
            if not FileUtility.exists(self.output_path+'/'+iso+'_'+trID+'.cloud.txt'):
                length=0
            else:
                length=len(FileUtility.load_list(self.output_path+'/'+iso+'_'+trID+'.cloud.txt'))
                report['language_iso'].append(iso)
                report['trans_ID'].append(trID)
                report['language_name'].append(self.id2lang_dict[trID])
                report['Description'].append(self.id2version[trID])
                report['verses'].append(length)
        report=pd.DataFrame(report)
        report.set_index('trans_ID')
        report.to_csv(self.output_path + '/reports/crawl_report_cloud.tsv', sep='\t', index=False, columns=['language_iso','trans_ID','language_name','Description','verses'])
        self.generate_final_rep()

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

