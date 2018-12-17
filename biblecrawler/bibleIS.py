__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__email__ = "asgari@berkeley.edu"
__project__ = "Super parallel project at CIS LMU"
__website__ = "https://llp.berkeley.edu/asgari/"

#!/usr/bin/env python3
import sys

sys.path.append('../')
from utility.file_utility import FileUtility
import os.path
import sys
import io
import lxml.html
import codecs
from multiprocessing import Pool
import tqdm
import re
from biblecrawler.general_crawler import BibleCrawler
from biblecrawler.general_parser import BibleParser
from lxml import etree
import requests
from utility.interface_util import query_yes_no

class BibleIS(BibleCrawler, BibleParser):
    '''
    Crawler for bible.cloud website
    '''
    log = []
    def __init__(self, triple, crawl=True, parse=True, remove_after_parse=False, printing=False):
        '''
        :param url:
        :param destination_directory:
        :param output_file:
        '''
        try:
            # get parameters
            self.url, self.destination_directory, output_file = triple
            self.output_file = self.destination_directory + output_file
            self.print = printing
            # crawl the pages
            # to be fixed
            if crawl:
                BibleCrawler.run_crawler(self, '//a[@class = "chapter-nav-right"]/@href', self.url, self.destination_directory)
            if parse:
                self.lang_directory = self.url.split('/')[3]
                # crawl the pages
                books=self.destination_directory + self.lang_directory
                self.run_parser(books, self.output_file)
                if remove_after_parse:
                    # parse the output file
                    # remove the directory
                    FileUtility.remove_dir(self.destination_directory + self.lang_directory)
        except:
            try:
                print(triple)
            except:
                return None
        return None

    @staticmethod
    def parallel_crawl(triples, num_p, override=False):
        '''
        :param triples:
        :param num_p:
        :param override:
        :return:
        '''
        if not override:
            new_list = []
            for x, y, z in triples:
                if not FileUtility.exists(y + z):
                    new_list.append((x, y, z))
            triples = new_list
        if len(triples) > 0:
            print('Start parallel crawling..')
            pool = Pool(processes=num_p)
            res = []
            for x in tqdm.tqdm(pool.imap_unordered(BibleIS, triples, chunksize=num_p), total=len(triples)):
                res.append(x)
            pool.close()
            FileUtility.save_list(triples[0][1] + 'log.txt', BibleIS.log)

    @staticmethod
    def sequential_crawl(triples, override=False):
        '''
        :param triples:
        :param override:
        :return:
        '''
        if not override:
            new_list = []
            for x, y, z in triples:
                if not FileUtility.exists(y + z):
                    new_list.append((x, y, z))
            triples = new_list

        print('Start crawling..')
        for x in tqdm.tqdm(triples):
            BibleIS(x)
        FileUtility.save_list(triples[0][1] + 'log.txt', BibleIS.log)

    def run_parser(self, basedir, outputfile):
        '''
        :param basedir:
        :param outputfile:
        :return:
        '''
        book2numbers = BibleParser.create_books2numbers(self)
        result = []
        for dirName, subdirList, fileList in os.walk(basedir):
            parts = os.path.split(dirName)
            if parts[-1].lower() not in book2numbers:
                if self.print:
                    print('skipping unknown directory', dirName, file=sys.stderr)
                continue
            book_number = book2numbers[parts[-1].lower()]
            for filename in fileList:
                chapter_number = filename.zfill(3)
                verses = self.parse_chapter(os.path.join(dirName, filename))
                result.extend((book_number + chapter_number + str(i).zfill(3), v) for i, v in verses)
        result.sort()

        f = codecs.open(outputfile, 'w', 'utf-8')
        for i, v in result:
            f.write('%s\t%s\n' % (i, ' '.join(w for w in v.split(' ') if w)))
        f.close()

    def parse_chapter(self, filename):
        '''
        :param filename:
        :return:
        '''
        verses = []
        last_v_number = -1
        v_number = None
        prev_open_bracket = False
        state = None
        text = ''

        # document = etree.parse(open(args[0]))
        try:
            document = lxml.html.parse(io.open(filename, encoding='utf8'))
        except UnicodeDecodeError as e:
            if self.print:
                print(filename, '\n', e, file=sys.stderr)
            document = lxml.html.parse(io.open(filename, encoding='utf8', errors='replace'))
        for event, element in etree.iterwalk(document, events=("start", "end")):
            if event == 'end' and state is not None and element.text is not None:
                text += element.text
            if event == 'start' and element.tag == 'span' \
                    and element.attrib.get('class', '') in ('verse-marker', 'verse-text'):
                state = element.attrib['class']
                text = ''
            elif event == 'end' and element.tag == 'span':
                if state == 'verse-marker':
                    v_number = int(text.strip())
                    state = None
                    text = None
                elif state == 'verse-text':
                    text = text.strip()
                    if prev_open_bracket:
                        text = '[' + text
                    if text.endswith('['):
                        prev_open_bracket = True
                        text = text.rstrip(' \t[')
                    else:
                        prev_open_bracket = False
                    if v_number == last_v_number:
                        _, t = verses.pop()
                        verses.append((v_number, t + ' ' + text.strip()))
                        if self.print:
                            print('Appending consecutive double verse numbers:', filename, v_number, file=sys.stderr)
                    else:
                        verses.append((v_number, text.strip()))
                    last_v_number = v_number
                    state = None
                    text = None
        return verses


if __name__ == '__main__':
    if requests.get("http://bible.is/robot.txt").status_code ==404:
        print ("No robot.txt found. Let's continue..")
    else:
        if query_yes_no("There is a robot.txt file at http://bible.is/robot.txt. Do you want to check manually your eligibility first?"):
            exit()
        else:
            print("OK, Let's continue..")
    triple = [(l.split()[1], '/mounts/data/proj/asgari/final_proj/000_datasets/testbib/bibleis_extra/', l.split()[0]) for l
              in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/biblis_extra_urls.txt')]
    BibleIS.parallel_crawl(triple, 30, True)
