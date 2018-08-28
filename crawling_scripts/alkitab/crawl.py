#!/usr/bin/env python3
"""Crawl bibles hosted on http://pngscriptures.org."""

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
        path_parts.pop()
        path_parts[-1] += '.html'
    dir_name = os.path.join(base_dir, *path_parts[1:-1])
    if not os.access(dir_name, os.F_OK):
        os.makedirs(dir_name)
    filename = os.path.join(dir_name, path_parts[-1])
    return filename


def save_response(response, tree, base_dir):
    filename = get_filename(response.url, base_dir)
    with open(filename, 'wb') as handle:
        handle.write(response.text.encode('utf8'))


def get_next_url(response, tree):
    xpath_result = list(set(tree.xpath('//a[@accesskey = "9"]/@href')))
    relevant = xpath_result[0] if len(xpath_result) == 1 else None
    if relevant:
        return urljoin(response.url, relevant)
    else:
        return None


def main(args):
    url = args[0]
    destination_directory = args[1]

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5'})
    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
    seen = set()
    chapters = []
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
        chapter_name = urlsplit(response.url)[-3]
        if chapters and chapters[-1] != chapter_name:
            chapters.append(chapter_name)
        
        tree = html.fromstring(response.content)
        save_response(response, tree, destination_directory)
        url = get_next_url(response, tree)
        if not url or not url.startswith('http'):
            print('Break on invalid url:', url, file=sys.stderr)
            break
        time.sleep(SLEEPTIME)
    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
    with open(os.path.join(destination_directory, 'chapters.txt'), 'w') as ch_file:
        for ch in chapters:
            ch_file.write(ch + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])
