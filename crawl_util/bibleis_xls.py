import requests
from bs4 import BeautifulSoup
import tqdm
import sys
sys.path.append('../')
from utility.file_utility import FileUtility
import pandas as pd


url_dict=dict()

#"https://find.bible/bibles/"
base_url = 'all_bibles.html'
f=open(base_url,'r')
soup = BeautifulSoup(f)
crawled=[]
for link in tqdm.tqdm(soup.select('a')):
    if 'href' in link.attrs:
        if 'https://find.bible/bibles/' in link.attrs['href'] and 'https://find.bible/bibles/search' not in  link.attrs['href']:
               crawled.append((link.attrs['href'].split('/')[-1],'\t'.join([x.text for x in link.find_parent().find_parent().select('td')])))

rows=[]
for x,y in crawled:
    a=[x]+y.split('\t')
    #if not len(a)==7:
    rows.append(a)

df=pd.DataFrame(rows,columns=['code','language','description','name','iso','date','country','name'])
cols=[idx for idx,x in enumerate(df.code.tolist()) if FileUtility.exists('/mounts/data/proj/asgari/final_proj/000_datasets/testbib/bibleis_extra/'+x+'/')]
df['bibleIS']=["http://www.bible.is/'"+df['code'].loc[x]+"'/Matt/1" if x in cols else 0 for x in range(len(df.code.tolist())) ]


writer = pd.ExcelWriter('xls/bibleis.xls', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Meta data')

# Close the Pandas Excel writer and output the Excel file.
writer.save()
