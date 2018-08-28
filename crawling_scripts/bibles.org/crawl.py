#!/usr/bin/env python3

import sys
import os.path
import time
import urllib.parse
import requests

SLEEPTIME = 4 #seconds

def save_response(response, base_dir, filename=None):
    if filename is None:
        parts = urllib.parse.urlsplit(response.url)
        path_parts = parts.path.split('/')
        if path_parts[-1] == '':
            path_parts[-1] = 'index.html'
        dir_name = os.path.join(base_dir, *path_parts[1:-1])
        filename = os.path.join(dir_name, path_parts[-1])
    else:
        dir_name = base_dir
        filename = os.path.join(base_dir, filename)
    if not os.access(dir_name, os.F_OK):
        os.makedirs(dir_name)
    with open(filename, 'wb') as f:
        if hasattr(response, 'content'):
            f.write(response.content)
        else:
            f.write(response.encode('utf8'))


def crawl_chapters(session, chapters, seen_chapters, destination_directory):
    for chapter in chapters:
        if chapter['id'] in seen_chapters:
            continue
        _bible_id, book_chapter = chapter['id'].split(':')
        url = 'http://bibles.org/chapters/%s.json' % chapter['id']
        headers = dict(Referer='http://bibles.org/' + chapter['link'])
        response = session.get(url, headers=headers)
        if response.status_code != requests.codes.ok:
            print('Error', time.strftime('%H:%M:%S'), url, response.url, response.status_code, file=sys.stderr)
            sys.exit(1)
        save_response(response, os.path.join(destination_directory, 'json_chapters'), filename=book_chapter+'.json')
        chapter = response.json()
        save_response(chapter['text'], os.path.join(destination_directory, 'chapters'), filename=book_chapter+'.html')
        seen_chapters.add(chapter['id'])
        #now save next chapter inluded in this response
        if 'nextChapter' in chapter:
            next_chapter = chapter['nextChapter']
            if not (next_chapter is None or next_chapter['id'] in seen_chapters):
                _bible_id, book_chapter = next_chapter['id'].split(':')
                save_response(next_chapter['text'], os.path.join(destination_directory, 'chapters'),
                              filename=book_chapter+'.html')
                seen_chapters.add(next_chapter['id'])
        time.sleep(SLEEPTIME)


def main(args):
    lang = args[0]
    destination_directory = args[1]

    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
                            'Accept': 'application/json, text/javascript, */*; q=0.01',
                            'X-Requested-With': 'XMLHttpRequest',
                            'Accept-Language': 'en-US,en;q=0.5'})

    print('Start time:', time.strftime('%H:%M:%S'), file=sys.stderr)

    url = 'http://bibles.org/versions/%s/books.json' % lang
    headers = dict(Referer='http://bibles.org/%s/Mat/1' % lang)
    response = session.get(url, headers=headers)

    if response.status_code != requests.codes.ok:
        print('Error', time.strftime('%H:%M:%S'), url, response.url, response.status_code, file=sys.stderr)
        sys.exit(1)
    save_response(response, destination_directory, 'books.json')
    seen_chapters = set()
    for book in response.json():
        bible_id, book_name = book['id'].split(':')
        url = 'http://bibles.org/books/%s/chapters.json' % book['id']
        print(book['id'])
        headers = dict(Referer='http://bibles.org/%s/%s/1' % (bible_id, book_name))
        response = session.get(url, headers=headers)
        if response.status_code != requests.codes.ok:
            print('Error', time.strftime('%H:%M:%S'), url, response.url, response.status_code, file=sys.stderr)
            sys.exit(1)
        save_response(response, destination_directory+'/books/', filename=book_name + '.json')
        crawl_chapters(session, response.json(), seen_chapters, destination_directory)
    print('End time', time.strftime('%H:%M:%S'), file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1:])
