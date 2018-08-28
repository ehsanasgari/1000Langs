#!/usr/bin/env python3

import sys
import os.path
import time
from urllib.parse import urljoin, urlsplit
import requests
from lxml import html, etree


SLEEPTIME = 4 #seconds


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


def save_response(response, tree, base_dir):
    parts = urlsplit(response.url)
    path_parts = parts.path.split('/')
    if path_parts[-1] == '':
        path_parts[-1] = 'index.html'
    dir_name = os.path.join(base_dir, *path_parts[1:-1])
    if not os.access(dir_name, os.F_OK):
        os.makedirs(dir_name)
    filename = os.path.join(dir_name, path_parts[-1])

    with open(filename, 'wb') as handle:
        handle.write(response.text.encode('utf-8')) # some bibles say utf-8, but they aren't. This will not work for all bibles here!


def get_next_url(response, tree):
    xpath_result = list(set(tree.xpath('//a[@title = "Next chapter"]/@href')))
    relevant = xpath_result[0] if len(xpath_result) >= 1 else None
    if relevant:
        return urljoin(response.url, relevant)
    else:
        return None


def main(args):
    url = args[0]
    destination_directory = args[1]

    session = requests.Session()
#    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
#                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#                            'Accept-Language': 'zh-pinyin,zh;q=0.5',
#                            'Accept-Charset': 'utf-8'})
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

        tree = html.fromstring(response.content)# might consider .text here
        save_response(response, tree, destination_directory)
        url = get_next_url(response, tree)
        if not url or not url.startswith('http'):
            print('Break on invalid url:', url, file=sys.stderr)
            break
        time.sleep(SLEEPTIME)
    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1:])
