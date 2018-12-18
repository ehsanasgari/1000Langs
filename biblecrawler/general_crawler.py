__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__website__ = "https://llp.berkeley.edu/asgari/"
__git__ = "https://github.com/ehsanasgari/"
__email__ = "ehsan.asgari@gmail.com"
__project__ = "1000Langs -- Super parallel project at CIS LMU"

#!/usr/bin/env python3
"""Crawl bibles hosted on http://pngscriptures.org."""
'''
This code is largely inspired/adapted from Michael Cysouw's crawling code
'''

import sys
sys.path.append('../')
import os.path
import sys
import time
import urllib
from urllib.parse import urljoin, urlsplit
from utility.file_utility import FileUtility
from utility.file_utility import FileUtility

import requests
from lxml import html


class BibleCrawler(object):
    SLEEPTIME = 0  # seconds
    log = []

    def run_crawler(self, nextpath, url, destination_directory, website='generic'):
        '''
        :param nextpath:
        :param url:
        :param destination_directory:
        :param website:
        :return:
        '''
        self.url=url
        self.nextpath = nextpath
        self.website = website
        self.counter=-1
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'Accept-Language': 'en-US,en;q=0.5'})
        if self.print:
            print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
        self.seen = set()
        self.useless_url = set()
        flag=True
        while flag:
            if (url in self.seen and  not self.website == 'PNG') or (self.website == 'PNG' and self.counter>=1188):
                if self.print:
                    print('Break on seen url:', url, file=sys.stderr)
                BibleCrawler.log.append('\t'.join(['Break on seen url:', str(url)]))
                flag=False
                break
            self.seen.add(url)
            if self.print:
                print(url)
            response = session.get(url)
            if response.status_code != requests.codes.ok:
                if self.print:
                    print('Error', url, response.url, response.status_code, file=sys.stderr)
                    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
                BibleCrawler.log.append(
                    '\t'.join([ 'Error', str(url), str(response.url), str(response.status_code)]))
                if self.website == 'PNG':
                    url=self.jump_url()
                    if not url:
                        flag=False
                        return
                else:
                    flag=False
                    return
            self.save_response(response, destination_directory)
            url = self.get_next_url(response)
            if not url or not url.startswith('http'):
                if self.print:
                    print('Break on invalid url:', url, file=sys.stderr)
                BibleCrawler.log.append('\t'.join(['Break on invalid url:', str(url)]))
                if self.website == 'PNG' and self.counter>=1188:
                    url=self.jump_url()
                else:
                    flag=False
                    break
            time.sleep(BibleCrawler.SLEEPTIME)
        if self.print:
            print(time.strftime('%H:%M:%S'), url, file=sys.stderr)

    def jump_url(self):
        '''
        :return:
        '''
        while self.counter < 1188:
            self.counter+=1
            url_select='/'.join(self.url.split('/')[0:-1])+'/'+FileUtility.load_list('../meta/pngscript_filenames.txt')[self.counter]
            if url_select not in self.seen and url_select not in self.useless_url:
                if requests.get(url_select).status_code==404:
                    if requests.get('/'.join(self.url.split('/')[0:-1])).status_code==404:
                        self.counter=1189
                        return None
                    self.useless_url.add(url_select)
                else:
                    url=url_select
                    self.useless_url.add(url)
                    return url
        return None

    def get_filename(self, url, base_dir):
        '''
        :param url:
        :param base_dir:
        :return:
        '''
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
        '''
        :param response:
        :param base_dir:
        :return:
        '''

        filename = self.get_filename(response.url, base_dir)

        if self.website == 'JW':
            # try to save only a part of the response
            tree = html.fromstring(response.content)
            text_divs = tree.xpath('//div[@id="bibleText"]')
            text_div = text_divs[0] if text_divs else None
            if text_div is not None:
                with open(filename, 'wb') as f:
                    f.write(etree.tostring(text_div))
            else:
                with open(filename, 'wb') as f:
                    f.write(handle.write(response.content))
        else:
            with open(filename, 'wb') as f:
                f.write(response.content)

    def get_next_url(self, response):
        tree = html.fromstring(response.content)
        if self.website == 'JW':
            link = tree.xpath('//div[@class="navLinkNext"]/a/@href')
            if link:
                url = urllib.parse.urljoin(response.url, link[0])
            else:
                url = None
            return url
        elif self.website == 'bible.com' or self.website=='bible.org':
            xpath_result = tree.xpath(
                '//a[contains(@class, "bible-nav-button nav-right fixed dim br-100 ba b--black-20 pa2 pa3-m flex items-center justify-center bg-white right-1")]//@href')
            relevant = xpath_result[0] if len(xpath_result) >= 1 else None
            # mydivs = soup.findAll("a", {"class": 'bible-nav-button nav-right fixed dim br-100 ba b--black-20 pa2 pa3-m flex items-center justify-center bg-white right-1'})
            # print ('Yes', 'bible-nav-button nav-right fixed dim br-100 ba b--black-20 pa2 pa3-m flex items-center justify-center bg-white right-1' in str(response.content))
        elif self.website == 'generic' or self.website == 'PNG':
            xpath_result = list(set(tree.xpath(self.nextpath)))
            relevant = xpath_result[0] if len(xpath_result) == 1 else None
        if relevant:
            return urljoin(response.url, relevant)
        else:
            return None
