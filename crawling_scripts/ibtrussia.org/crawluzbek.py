#!/usr/bin/env python3
"""Crawl bibles hosted on http://ibtrussia.org"""

import sys
import os.path
import re
import time
from urllib.parse import urljoin, urlsplit
import requests
from lxml import html, etree


SLEEPTIME = 1 #seconds


def get_filename(url, base_dir):
    """Derive a filename from the given URL"""

    parts = urlsplit(url)
    path_parts = parts.path.split('/')
    if path_parts[-1] == '':
        path_parts[-1] = 'index.html'
    dir_name = os.path.join(base_dir, *path_parts[1:-1])
    if not os.access(dir_name, os.F_OK):
        os.makedirs(dir_name)
    filename = os.path.join(dir_name, path_parts[-1])
    return filename

# def save_response(response, base_dir):
#     filename = get_filename(response.url, base_dir)
#     with open(filename, 'wb') as handle:
#         handle.write(response.content)

def save_response(response, tree, base_dir):
    parts = urlsplit(response.url)
    
    query = parts[3]
    chapter = re.sub('l=','', query.split('&')[1])
    filename = os.path.join(base_dir, chapter)
    
#    path_parts = parts.path.split('/')
#    if path_parts[-1] == '':
#        path_parts[-1] = 'index.html'
#    dir_name = os.path.join(base_dir, *path_parts[1:-1])
#    if not os.access(dir_name, os.F_OK):
#        os.makedirs(dir_name)
#    filename = os.path.join(dir_name, path_parts[-1])

    #try to save only a part of the response
    xpath_result = tree.xpath('//div[@class="text"]')
    relevant = xpath_result[0] if len(xpath_result) == 1 else None
    with open(filename, 'wb') as handle:
        if relevant is not None:
            handle.write(etree.tostring(relevant))#, encoding='utf8'))
        else:
            handle.write(response.text.encode('utf8'))

def get_next_url(url, tree):
    xpath_result = tree.xpath('//div[@class="prevnext"]//a[@title="Keyingi bob" or @title="Кейинги боб"]/@href')
    if len(xpath_result) > 0:
        relevant = xpath_result[0].split('&')[1]
        return re.sub('l=.+\.*\d*',relevant,url)
    else:
        book = tree.xpath('//select[@id="selbook"]/option[@selected="selected"]/following-sibling::option[1]/@value')
        if len(book) > 0:
            book = book[0]
            return re.sub('l=.+\.\d+','l='+book+'.1',url)


def main(args):
    url = args[0]
    destination_directory = args[1]

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5'})
    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
    seen = set()
    while True:
        if url in seen: #basic safety to prevent infinite loop
            print('Break on seen url:', url, file=sys.stderr)
            break
        seen.add(url)
        print(url)
        response = session.get(url)
        if response.status_code != requests.codes.ok:
            print('Error', url, response.url, response.status_code, file=sys.stderr)
            print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
            sys.exit(1)

        tree = html.fromstring(response.text) # or "response.content"
        save_response(response, tree, destination_directory)
        url = get_next_url(response.url, tree)
        if not url or not url.startswith('https'):
            print('Break on invalid url:', url, file=sys.stderr)
            break
        time.sleep(1)
    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1:])
