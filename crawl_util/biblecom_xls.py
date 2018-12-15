import requests
from bs4 import BeautifulSoup
import tqdm
import sys
sys.path.append('../')
from utility.file_utility import FileUtility
import pandas as pd

def get_metadata(node):
    iso=''
    description=''
    for x in node.parent.parent.parent.select("a[class^='lang_title']"):
        iso=x['href'].split('/')[-1]
    description=' '.join(node.parent.select('a')[0]['href'].split('/')[-1].split('-')[1::])
    num=node.parent.select('a')[0]['href'].split('/')[-1].split('-')[0]
    return iso, description, num

base_url = 'https://www.bible.com/versions'
soup = BeautifulSoup(requests.get(base_url).content)
# collect the game ids
collect_version_links=dict()
for link in tqdm.tqdm(soup.select('a[target^=_self]')):
    if 'href' in link.attrs:
        if 'versions' in link.attrs['href']:
            iso,descript,num=get_metadata(link)
            collect_version_links['https://www.bible.com'+link.attrs['href']]=(iso,descript,num)
            
final_list=[]
langs=[]
for url,meta in tqdm.tqdm(collect_version_links.items()):
    soup_inner = BeautifulSoup(requests.get(url+'.html').content)
    for lang in soup_inner.select('h2[class^=version]'):
        for x in lang.children:
            if ('<div>' in str(x)):
                langs.append(str(x).replace('<div>','').replace('</div>',''))
    for lang in soup_inner.select("a[class^='solid-button mobile-full blue']"):
        final_list.append(['https://www.bible.com'+lang.attrs['href']]+list(meta)+[langs[-1]])
        
df=pd.DataFrame(final_list,columns=['url','iso','description','num','language'])

df=pd.DataFrame(df, columns=['iso','language','description','num','url'])

writer = pd.ExcelWriter('xls/bible_com.xls', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Meta data')

# Close the Pandas Excel writer and output the Excel file.
writer.save()

isos=(set(df[df['Exist']==True]['iso'].tolist()))
iso_michael=[x.split('/')[-1][0:3] for x in FileUtility.recursive_glob('/mounts/data/proj/asgari/superparallelproj/paralleltext/bibles/corpus','*.txt')]
