import requests
from bs4 import BeautifulSoup
import tqdm
import sys
import pandas as pd
sys.path.append('../')
from utility.file_utility import FileUtility
from pandas import Series
from bdpAPI.bdpcall import BDPCall

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

global meta_data_paths
meta_data_paths={'allbiblexls':'0meta/main.xls','iso_file':'0meta/ISO639-3.tsv', 'final_file': '0meta/meta.tsv'}


def getMetaEbible():
    base_url = 'http://ebible.org/Scriptures/copyright.php'
    soup = BeautifulSoup(requests.get(base_url).content)
    tables=[]
    for link in soup.select('table'):
        tables.append(pd.read_html(str(link),header=0)[0])
    results=pd.concat(tables,sort=True)


    mask=(results['FCBH/DBS'].str.len() == 6) & (results['FCBH/DBS'].str.isupper())
    df = results.loc[mask]
    df['iso']=[x[0:3] for x in df['ID'].tolist()]
    df=df[['iso','FCBH/DBS','Language','Language in English', 'Year','Short Title']]
    return df

def getMetaFindBible():
    global meta_data_paths

    df_main=pd.read_excel(meta_data_paths['allbiblexls'])
    df_main=df_main.rename(index=str, columns={"code": "FCBH/DBS", "language": "Language",'description':'Short Title','date':'Year'})
    return df_main

def getMetaMerged():
    global meta_data_paths

    # read and merge two bibles
    df_ebible=getMetaEbible()
    df_main=getMetaFindBible()
    df=pd.concat([df_ebible[['iso','FCBH/DBS','Language','Year','Short Title']],df_main[['iso','FCBH/DBS','Language','Year','Short Title']]])
    df=df.rename(index=str, columns={"Short Title": "description",'iso':'ISO'})

    # get metadata from ISO Rec
    df_iso=pd.read_table(meta_data_paths['iso_file'])
    iso_dict=Series(df.Language.values,index=df.ISO).to_dict()
    iso_dict.update(Series(df_iso.NAM_LABEL.values,index=df_iso.ISO).to_dict())
    df["Language"] = df["ISO"].map(lambda x:iso_dict[x])

    # set the key
    df=df.set_index('FCBH/DBS')
    return df

def create_meta_data(apikey='f03a423aad95120f8eb40005070f19e9',path='/mounts/data/proj/asgari/final_proj/000_datasets/testbib/API_new_Res'):
    global meta_data_paths
    df=getMetaMerged()
    # check on the API
    BDP_API=BDPCall(apikey)
    IDS=df.index.tolist()
    IDS.sort()
    existOnAPI=BDP_API.doesExist_bibleIDS(path,IDS,20)
    df['exist_API']=df.index.map(lambda x:existOnAPI[x])
    df.to_csv(meta_data_paths['final_file'] ,sep='\t')

def update_meta_data(apikey='f03a423aad95120f8eb40005070f19e9',path='/mounts/data/proj/asgari/final_proj/000_datasets/testbib/API_new_Res'):
    global meta_data_paths
    df=pd.read_table(meta_data_paths['final_file'])
    # check on the API
    BDP_API=BDPCall(apikey)
    IDS=df.index.tolist()
    IDS.sort()
    existOnAPI=BDP_API.doesExist_bibleIDS(path,IDS,20)
    df['exist_API']=df.index.map(lambda x:existOnAPI[x])
    df.to_csv(meta_data_paths['final_file'] ,sep='\t')

def crawl_bibles(apikey='f03a423aad95120f8eb40005070f19e9',path='/mounts/data/proj/asgari/final_proj/000_datasets/testbib/API_new_Res'):
    BDP_obj = BDPCall(apikey)
    BDP_obj.crawl_bible_books(path,10)
