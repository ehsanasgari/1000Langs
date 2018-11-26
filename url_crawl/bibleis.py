import requests
from bs4 import BeautifulSoup
import tqdm
import sys
sys.path.append('../')
from utility.file_utility import FileUtility

url_dict=dict()

#"https://find.bible/bibles/"
base_url = '/mounts/data/proj/asgari/final_proj/1000langs/config/all_bibles.html'
f=open(base_url,'r')
soup = BeautifulSoup(f)
crawled=[]
for link in tqdm.tqdm(soup.select('a')):
    if 'href' in link.attrs:
        if 'https://find.bible/bibles/' in link.attrs['href'] and 'https://find.bible/bibles/search' not in  link.attrs['href']:
               crawled.append((link.attrs['href'].split('/')[-1],'\t'.join([x.text for x in link.find_parent().find_parent().select('td')])))

FileUtility.save_list('/mounts/data/proj/asgari/final_proj/1000langs/config/biblis_extra.txt',['\t'.join(list(x)) for x in crawled])

ids=[x.split()[1].split('bible.is/')[1].split('/')[0] for x in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/finalized_urls/bibleis.txt')]
intersect=set(list(dict(crawled).keys())).intersection(ids)
new_urls=[idx+'.txt\t'+'http://www.bible.is/'+idx+'/Matt/1' for idx in list(dict(crawled).keys()) if idx not in intersect]
FileUtility.save_list('/mounts/data/proj/asgari/final_proj/1000langs/config/biblis_extra_urls.txt',new_urls)
