import requests
from bs4 import BeautifulSoup
import tqdm
import sys
sys.path.append('../')
from utility.file_utility import FileUtility
import pandas as pd
import numpy as np

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
