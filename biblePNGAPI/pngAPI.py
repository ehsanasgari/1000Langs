__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__email__ = "asgari@berkeley.edu"
__project__ = "Super parallel project at CIS LMU"
__website__ = "https://llp.berkeley.edu/asgari/"

import re
import requests
from bs4 import BeautifulSoup
import tqdm
import sys
sys.path.append('../')
from utility.file_utility import FileUtility
import validators
import requests, zipfile, io
from multiprocessing import Pool
import pandas as pd
from biblecrawler.biblePngscripturesORG import PNGScriptRetrieve

class PNGAPl(object):
    '''
        PBC retrieving from the PNG scripture
    '''
    def __init__(self, output_path):
        '''
            Constructor
        '''
        # set the parameters
        self.output_path = output_path
        FileUtility.ensure_dir(self.output_path + '/pngscripture_intermediate/')
        FileUtility.ensure_dir(self.output_path + '/reports/')
        def warn(*args, **kwargs):
            pass
        import warnings
        warnings.warn = warn

    def crawl_bpc(self,nump=20):
        self.find_all_languages_on_png()
        self.crawl_all_found_langs(nump)
        self.create_report_png()

    def download_zipfile(self, url_outpath_rec):
        try:
            url, outpath, iso, code, langname=url_outpath_rec
            FileUtility.ensure_dir(outpath)
            r = requests.get(url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(outpath)
            temp=PNGScriptRetrieve((url,outpath,'../../'+iso+'_'+code.replace('_','-')+'.png.txt'), crawl=False, parse=True)
            return url, [iso,code.replace('_','-'),langname]
        except:
            return url, False

    def find_all_languages_on_png(self):
        url_dict=dict()
        base_url = 'http://pngscriptures.org/'
        soup = BeautifulSoup(requests.get(base_url).content)
        for link in tqdm.tqdm(soup.select('div[class^=button]')):
            for links in link.select('a'):
                code=links.attrs['href'][0:-1]
                iso=code[0:3]
                if not validators.url(code):
                    url_dict[links.attrs['href'][0:-1]]=(iso,code, 'http://pngscriptures.org/'+links.attrs['href']+links.attrs['href'][0:-1]+'_html.zip',re.sub(" *\\(.*", "", link.text))
        self.url_dict=url_dict

    def crawl_all_found_langs(self,nump=20):
        table=[]
        inputs=[]
        for code, rec in tqdm.tqdm(self.url_dict.items()):
            inputs.append((rec[2],self.output_path+'/pngscripture_intermediate/'+rec[1]+'/',rec[0],rec[1],rec[3]))
        res=PNGAPl.make_parallel(nump,self.download_zipfile, inputs)
        for x,y in res.items():
            if y:
                table.append(y)
        self.df_png=pd.DataFrame(table)
        self.df_png=self.df_png.rename(index=str,columns={0:'language_iso',1:'trans_ID',2:'language_name'})


    @staticmethod
    def make_parallel(num_p, func, in_list):
        pool = Pool(processes=num_p)
        final_res = dict()
        for idx, res in tqdm.tqdm(pool.imap_unordered(func, in_list, chunksize=num_p), total=len(in_list)):
            final_res[idx] = res
        pool.close()
        return final_res

    def create_report_png(self):
        self.df_png['verses']=0

        png_files=FileUtility.recursive_glob(self.output_path+'/', '*.png.txt')
        for png_file in png_files:
            iso,code=png_file.split('/')[-1].split('.')[0:-1][0:-1][-1].split('_')
            length=len(FileUtility.load_list(png_file))
            self.df_png.loc[:,'verses'][(self.df_png['language_iso']==iso) & (self.df_png['trans_ID']==code)]=length
        self.df_png.set_index('trans_ID')
        self.df_png.to_csv(self.output_path + '/reports/crawl_report_png.tsv', sep='\t', index=False, columns=['language_iso','trans_ID','language_name','verses'])
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

