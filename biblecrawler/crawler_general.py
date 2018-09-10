#!/usr/bin/env python3
"""Crawl bibles hosted on http://pngscriptures.org."""

import os.path
import sys
import time
from urllib.parse import urljoin, urlsplit

import requests
from lxml import html


class BibleCrawler(object):
    SLEEPTIME = 0  # seconds
    log = []
    def run_crawler(self, nextpath, url, destination_directory):

        self.nextpath=nextpath

        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'Accept-Language': 'en-US,en;q=0.5'})
        if self.print:
            print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
        seen = set()
        while True:
            if url in seen:
                if self.print:
                    print('Break on seen url:', url, file=sys.stderr)
                BibleCrawler.log.append('\t'.join([self.output_file, 'Break on seen url:', str(url)]))
                break
            seen.add(url)
            if self.print:
                print(url)
            response = session.get(url)
            if response.status_code != requests.codes.ok:
                if self.print:
                    print('Error', url, response.url, response.status_code, file=sys.stderr)
                    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
                BibleCrawler.log.append(
                    '\t'.join([self.output_file, 'Error', str(url), str(response.url), str(response.status_code)]))
                return
            self.save_response(response, destination_directory)
            url = self.get_next_url(response)
            if not url or not url.startswith('http'):
                if self.print:
                    print('Break on invalid url:', url, file=sys.stderr)
                BibleCrawler.log.append('\t'.join([self.output_file, 'Break on invalid url:', str(url)]))
                break
            time.sleep(BibleCrawler.SLEEPTIME)
        if self.print:
            print(time.strftime('%H:%M:%S'), url, file=sys.stderr)

    def get_filename(self, url, base_dir):
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

    def save_response(self, response, base_dir):
        filename = self.get_filename(response.url, base_dir)
        with open(filename, 'wb') as f:
            f.write(response.content)

    def get_next_url(self, response):
        tree = html.fromstring(response.content)
        xpath_result = list(set(tree.xpath(self.nextpath)))
        relevant = xpath_result[0] if len(xpath_result) == 1 else None
        if relevant:
            return urljoin(response.url, relevant)
        else:
            return None

