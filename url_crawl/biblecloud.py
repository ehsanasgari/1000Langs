import requests
from bs4 import BeautifulSoup
import tqdm
import sys
sys.path.append('../')
from utility.file_utility import FileUtility



base_url = 'https://bible.cloud/inscript/content/texts/'
soup = BeautifulSoup(requests.get(base_url).content)

# collect the game ids
collect_version_links=[]
langs=[]
url_dict=dict()
for link in tqdm.tqdm(soup.select('a')):
    #soup_inner = BeautifulSoup(requests.get(link).content)
    #soup.select('a[href^=https://www.bible.com/versions/*]'):
    if 'class' in link.attrs:
        if len(link.contents)==1:
            if 'href' in link.attrs:
                url_dict[link.contents[0].replace(' ','-')]='https://bible.cloud/inscript/content/texts/'+link.attrs['href'].replace('index.html','MT1.html')

urls=list(url_dict.keys())
urls.sort()
FileUtility.save_list('/mounts/data/proj/asgari/final_proj/1000langs/config/extra_handled_bible.cloud.txt',['\t'.join([url.replace(' ','').replace('\t',''),url_dict[url]]) for url in urls])
