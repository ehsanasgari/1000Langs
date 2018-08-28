#!/usr/bin/env python3

import sys
import os.path
import random
import time
import urllib.parse
import requests
from lxml import html


SLEEPTIME = 1 #seconds


def get_filename(url, base_dir):
    parts = urllib.parse.urlsplit(url)
    path_parts = parts.path.split('/')
    if path_parts[-1] == '':
        path_parts[-1] = 'index.html'
    dir_name = os.path.join(base_dir, *path_parts[1:-1])
    if not os.access(dir_name, os.F_OK):
        os.makedirs(dir_name)
    filename = os.path.join(dir_name, path_parts[-1])
    return filename


def save_response(response, base_dir):
    parts = urllib.parse.urlsplit(response.url)
    path_parts = parts.path.split('/')
    if path_parts[-1] == '':
        path_parts[-1] = 'index.html'
    dir_name = os.path.join(base_dir, *path_parts[1:-1])
    if not os.access(dir_name, os.F_OK):
        os.makedirs(dir_name)
    filename = os.path.join(dir_name, path_parts[-1])
    with open(filename, 'wb') as handle:
        handle.write(response.content)


def parse_overview(response):
    """Parse overview page.

    All links with attribute target="_top" lead to a book
    """

    tree = html.fromstring(response.content)
    links = tree.xpath('//a[@target="_top"]/@href')
    return [urllib.parse.urljoin(response.url, l) for l in links]


def parse_book_listing(response):
    """Parse directory listing of a particular book for chapter links.
    
    Every link which ends with '.htm' has to be fetched.
    """
    tree = html.fromstring(response.content)
    links = tree.xpath('//a/@href')
    return [urllib.parse.urljoin(response.url, l) for l in links if l.endswith('.htm')]


def fetch_book(book_url, session, referer, destination_directory):
    time.sleep(SLEEPTIME + 0.1*random.randint(0, 10*SLEEPTIME))
    #strip the last part of the URL to fetch directory overview
    url = book_url[:book_url.rfind('/')+1]
    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
    response = session.get(url, headers={'referer': referer})
    if response.status_code != requests.codes.ok:
        print('Error', url, response.url, response.status_code, file=sys.stderr)
        sys.exit(1)
    chapters = parse_book_listing(response)
    referer = book_url
    for c in chapters:
        referer = fetch_chapter(c, session, referer, destination_directory)


def fetch_chapter(chapter_url, session, referer, destination_directory):
    filename = get_filename(chapter_url, destination_directory)
    if os.access(filename, os.F_OK):
        print('skipping existing file', chapter_url, filename, file=sys.stderr)
        return referer
    time.sleep(SLEEPTIME + 0.1*random.randint(0, 10*SLEEPTIME))
    print(time.strftime('%H:%M:%S'), chapter_url, file=sys.stderr)
    response = session.get(chapter_url, headers={'referer': referer})
    if response.status_code != requests.codes.ok:
        print('Error', chapter_url, response.url, response.status_code, file=sys.stderr)
        sys.exit(1)
    save_response(response, destination_directory)
    return response.url


def main(args):
    bible = args[0]
    destination_directory = args[1]

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5'})
    url = urllib.parse.urljoin('http://bibeltext.com', bible +  '/')
    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
    response = session.get(url)
    if response.status_code != requests.codes.ok:
        print('Error', url, response.url, response.status_code, file=sys.stderr)
        sys.exit(1)
    books = parse_overview(response)
    for book in books:
        fetch_book(book, session, response.url, destination_directory)


if __name__ == '__main__':
    main(sys.argv[1:])
