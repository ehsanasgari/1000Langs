__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__website__ = "https://llp.berkeley.edu/asgari/"
__git__ = "https://github.com/ehsanasgari/"
__email__ = "ehsan.asgari@gmail.com"
__project__ = "1000Langs -- Super parallel project at CIS LMU"

import requests
from bs4 import BeautifulSoup
import tqdm
import sys
sys.path.append('../')
from utility.file_utility import FileUtility
import pandas as pd
import numpy as np
from massive_parallelbible_IF.accessbible import AccessBible

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

def getMetaFindBible():
    #"https://find.bible/bibles/"
    base_url = '../meta/bibles_list.html'
    f=open(base_url,'r')
    soup = BeautifulSoup(f)
    table=soup.select('table')[0]
    df=pd.read_html(table.prettify(), flavor='bs4',header=0)[0]
    res = [[np.where(tag.has_attr('href'),tag.get('href'),"no link") for tag in tagr.find_all('a')] for tagr in table.find_all('tr')]
    df['trans_ID'] = ['Not Available' if x==[] else x[0].tolist().split('/')[-1]  for x in res[1::]]
    df=df.rename(index=str,columns={x:x.strip() for x in df.columns.tolist()})
    df=df.rename(index=str,columns={'Name':'Description','Date':'Year','ISO':'language_iso','Language':'language_name'})
    df=df[['trans_ID','language_iso','language_name','Description','Year']]
    df=df[df['trans_ID']!='Not Available']
    df.set_index('trans_ID')
    return df

def getMetaEbible():
    base_url = 'http://ebible.org/Scriptures/copyright.php'
    soup = BeautifulSoup(requests.get(base_url).content)
    tables=soup.select('table')
    dfs=[]
    for table in tables:
        dfs.append(pd.read_html(table.prettify(), flavor='bs4',header=0)[0])
    df=pd.concat(dfs, sort=True)
    mask=(df['FCBH/DBS'].str.len() == 6) & (df['FCBH/DBS'].str.isupper())
    df = df.loc[mask]
    df['iso']=[x[0:3] for x in df['ID'].tolist()]
    df=df[['iso','FCBH/DBS','Language in English', 'Year','Short Title']]
    df=df.rename(index=str,columns={'iso':'language_iso','FCBH/DBS':'trans_ID','Language in English':'language_name','Short Title':'Description','Date':'Year'})
    df=df[['trans_ID','language_iso','language_name','Description','Year']]
    df.set_index('trans_ID')
    return df

def getMetaMerged():
    # read and merge two bibles
    df_ebible=getMetaEbible()
    df_main=getMetaFindBible()
    df=pd.concat([df_main,df_ebible])
    df.drop_duplicates(subset=['trans_ID'], keep='last', inplace=True)
    df.set_index('trans_ID')
    return df

def getMassiveparallel_meta(update=False):
    errors=[]
    if update:
        # Get michael's corpora
        AccBible = AccessBible(AccessBible.path)
        massive_par_corpora=AccBible.get_list_of_all_lang_translations()
        massive_par_corpora_length=dict()
        for lang, trnsls in tqdm.tqdm(massive_par_corpora.items()):
            length_list=[]
            for trns in trnsls:
                try:
                    l=len(AccBible.get_subcorpus_bible_by_lang_trans_filtered(lang,trns))
                    length_list.append(l)
                except:
                    errors.append((lang,trns))
            if length_list!=[]:
                massive_par_corpora_length[lang]=(len(length_list),max(length_list),np.mean(length_list))
        rows=[]
        for iso, scores in massive_par_corpora_length.items():
            rows.append([iso, scores[0], scores[1], scores[2]])
        df=pd.DataFrame(rows)
        df=df.rename(index=str, columns={0:'language_iso',1:'#trans-massivepar', 2:'max-verse-massivepar',3:'mean-verse-massivepar'})
        df=df.set_index('language_iso')
        df.to_csv('../meta/massive_par_stat.tsv', sep='\t', index=True)
    return pd.read_table('../meta/massive_par_stat.tsv', sep='\t')
