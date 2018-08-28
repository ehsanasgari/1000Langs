from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import requests
import w3lib.html
from w3lib.html import remove_tags

def parse_url(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def getBible_trans_names():
    lang_names=dict()
    lang_bible_dict=dict()
    raw_html = parse_url('http://ebible.org/download.php')
    html = BeautifulSoup(raw_html, 'html.parser')
    for i, li in enumerate(html.select('tr')):
        for j, lj in enumerate(li.select('td')):
            if j==2:
                col=lj.select('a')[0]['href']
                if '=' in col:
                    if len(col.split('=')[1]) > 2:
                        isocode=col.split('=')[1][0:3]
                        name=col.split('=')[1]
                        if isocode not in lang_bible_dict:
                            lang_bible_dict[isocode]=[name]
                            lang_names[isocode]=lj.text
                        else:
                            lang_bible_dict[isocode].append(name)

    return lang_bible_dict, lang_names


def getNewtestamentBooks():
    webpage='http://ebible.org/eng-webbe/'
    raw_html = parse_url(webpage)
    html = BeautifulSoup(raw_html, 'html.parser')
    elements=html.find_all("a", class_="nn")
    urls = [a['href'][0:3] for a in elements]

    chapter_dict=dict()
    for url in urls:
        counter=1
        address=webpage+url+'0'+str(counter)+'.htm'
        request = requests.get(address)
        while request.status_code == 200:
            counter+=1
            address=webpage+url+('0' if counter <10 else ('')) +str(counter)+'.htm'
            request = requests.get(address)
        chapter_dict[url]=counter
    books={'MAT': 28, 'MRK': 16, 'LUK': 24, 'JHN': 21, 'ACT': 28, 'ROM': 16, '1CO': 16, '2CO': 13,'GAL': 6,
    'EPH': 6,'PHP': 4, 'COL': 4,'1TH':5,'2TH' :3,'1TI' :6,'2TI': 4,'TIT': 3,'PHM': 1,'HEB': 13,'JAS': 5,'1PE': 5,'2PE': 3,'1JN': 5,'2JN': 1,'3JN': 1,'JUD': 1,'REV': 22}

def scrapeVerses(lang, book, chapter):
    verse_dict=dict()
    webpage='http://ebible.org/'+lang+'/'+book+chapter+'.htm'
    raw_html = parse_url(webpage)
    html = BeautifulSoup(raw_html, 'html.parser')
    elements=html.find_all("div", class_="p")
    for el in elements:
        for span in el.find_all("span", class_='verse'):
            VID=span['id']
            print(VID)
            text=''
            for tag in span.next_siblings:
                if tag.name == "span":
                    print(text)
                    verse_dict[VID]=text
                    break
                else:
                    text += remove_tags(str(tag))
    return verse_dict


print(scrapeVerses('pesOPV', 'MAT', '01'))

