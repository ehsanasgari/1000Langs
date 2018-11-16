import requests
from bs4 import BeautifulSoup
import tqdm
import sys
sys.path.append('../')
from utility.file_utility import FileUtility

base_url = 'https://www.bible.com/versions'
soup = BeautifulSoup(requests.get(base_url).content)
# collect the game ids
collect_version_links=[]
langs=[]
url_dict=dict()
for link in tqdm.tqdm(soup.select('a[target^=_self]')):
    #soup_inner = BeautifulSoup(requests.get(link).content)
    #soup.select('a[href^=https://www.bible.com/versions/*]'):
    if 'href' in link.attrs:
        if 'versions' in link.attrs['href']:
            collect_version_links.append('https://www.bible.com'+link.attrs['href'])

for url in tqdm.tqdm(collect_version_links):
    soup_inner = BeautifulSoup(requests.get(url+'.html').content)
    for lang in soup_inner.select('h2[class^=version]'):
        for x in lang.children:
            if ('<div>' in str(x)):
                langs.append(str(x).replace('<div>','').replace('</div>',''))
    for lang in soup_inner.select("a[class^='solid-button mobile-full blue']"):
        url_dict[langs[-1]]='https://www.bible.com'+lang.attrs['href']

urls=list(url_dict.keys())
urls.sort()
FileUtility.save_list('/mounts/data/proj/asgari/final_proj/1000langs/config/extra_handled_bible.com.txt',['\t'.join([url.replace(' ','').replace('\t',''),url_dict[url]]) for url in urls])

