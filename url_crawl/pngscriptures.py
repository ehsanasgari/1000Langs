import requests
from bs4 import BeautifulSoup
import tqdm
import sys
sys.path.append('../')
from utility.file_utility import FileUtility

url_dict=dict()

base_url = 'http://pngscriptures.org/'
soup = BeautifulSoup(requests.get(base_url).content)
for link in tqdm.tqdm(soup.select('div[class^=button]')):
    for links in link.select('a'):
        url_dict[links.attrs['href'][0:-1]]='http://pngscriptures.org/'+links.attrs['href']+'MAT01.htm'

urls=list(url_dict.keys())
urls.sort()
FileUtility.save_list('/mounts/data/proj/asgari/final_proj/1000langs/config/extra_handled_pngscriptures.txt',['\t'.join([url.replace(' ','').replace('\t',''),url_dict[url]]) for url in urls])

