#!/usr/bin/env python3

import sys
import os.path
import time
import urllib.parse
import requests
from lxml import html, etree

SLEEPTIME = 3 #seconds


def get_filename(url, base_dir):
    parts = urllib.parse.urlsplit(url)
    path_parts = parts.path.split('/')
    if path_parts[-1] == '':
        path_parts.pop()
        if not path_parts:
            path_parts.append('index.html')
        else:
            path_parts[-1] += '.html'
    if len(path_parts) > 3: #strip language specific parts
        path_parts[2:4] = []
    dir_name = os.path.join(base_dir, *path_parts[1:-1])
    if not os.access(dir_name, os.F_OK):
        os.makedirs(dir_name)
    filename = os.path.join(dir_name, path_parts[-1])
    return filename


def save_response(response, base_dir):
    filename = get_filename(response.url, base_dir)

    #try to save only a part of the response
    tree = html.fromstring(response.content)
    text_divs = tree.xpath('//div[@id="bibleText"]')
    text_div = text_divs[0] if text_divs else None

    with open(filename, 'wb') as handle:
        if text_div is not None:
            handle.write(etree.tostring(text_div))
        else:
            handle.write(response.content)


def get_next_url(response):
    tree = html.fromstring(response.content)
    link = tree.xpath('//div[@class="navLinkNext"]/a/@href')
    if link:
        url = urllib.parse.urljoin(response.url, link[0])
    else:
        url = None
    return url


def get_book_numbers(session, url):
    response = session.get(url)
    if response.status_code != requests.codes.ok:
        print('Error', url, response.url, response.status_code, file=sys.stderr)
        print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
        sys.exit(1)
    tree = html.fromstring(response.content)
    url_list = tree.xpath('//form[@class="clearfix"]/@action')
    url = None if not url_list else urllib.parse.urljoin(response.url, url_list[0])
    book_numbers = tree.xpath('//select[@id="Book"]/option/@value')

    return url, book_numbers


def main(args):
    single_run = (args[0] == '-s')
    if single_run:
        args.pop(0)
    url = args[0]
    destination_directory = args[1]

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5'})
    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)

    entry_url, book_numbers = get_book_numbers(session, url)
    if not entry_url:
        print('Did not find entry URL in form', file=sys.stderr)
        sys.exit(1)

    seen = set()
    for book in book_numbers:
        if not single_run:
            url = entry_url + ('?Book=%s&Chapter=1' % book)
        while True:
            if url in seen:
                print('Break on seen url:', url, file=sys.stderr)
                break
            seen.add(url)
            print(url)
            sys.stdout.flush()
            response = session.get(url)
            if response.status_code != requests.codes.ok:
                print('Error', url, response.url, response.status_code, file=sys.stderr)
                print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
                sys.exit(1)
            if 'We are temporarily off-line.' in response.text:
                print('Server offline; sleeping 60s.', file=sys.stderr)
                seen.remove(url)
                time.sleep(60)
                continue
            save_response(response, destination_directory)

            url = get_next_url(response)
            if not url or not url.startswith('http'):
                print('Break on invalid url:', url, file=sys.stderr)
                break
            time.sleep(1)
        print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
        if single_run:
            break


if __name__ == '__main__':
    main(sys.argv[1:])
