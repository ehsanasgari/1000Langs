#!/usr/bin/env python3
import sys
sys.path.append('../')
from utility.file_utility import FileUtility
import os.path
import sys
import time
from urllib.parse import urljoin, urlsplit
import requests
from lxml import html
import io
import lxml.html
from lxml import etree
import codecs
from multiprocessing import Pool
import tqdm
import re
from biblecrawler.general_crawler import BibleCrawler
from biblecrawler.general_parser import BibleParser
import requests
from utility.interface_util import query_yes_no

class PNGScriptCrawl(BibleCrawler,BibleParser):
    log=[]

    def __init__(self, triple, crawl=True, parse=True, remove_after_parse=False, printing=False):
        '''
        :param url:
        :param destination_directory:
        :param output_file:
        '''
        # get parameters
        self.url, self.destination_directory, output_file=triple
        self.output_file=self.destination_directory + output_file
        self.print=printing
        # find the lang ID in the website
        self.lang_directory = self.url.split('/')[3]
        if crawl:
            # crawl the pages
            BibleCrawler.run_crawler(self,'//a[text() = ">"]/@href',self.url, self.destination_directory, website='PNG')
        if parse:
            # parse the output file
            books=self.destination_directory + self.lang_directory
            self.run_parser(books, self.output_file)
            if remove_after_parse:
                FileUtility.remove_dir(self.destination_directory + self.lang_directory)
        return None

    @staticmethod
    def parallel_crawl(triples, num_p, override=False):
        if not override:
            new_list=[]
            for x,y,z in triples:
                if not FileUtility.exists(y+z):
                    new_list.append((x,y,z))
            triples=new_list
        if len(triples)>0:
            print ('Start parallel crawling..')
            pool = Pool(processes=num_p)
            res=[]
            for x in tqdm.tqdm(pool.imap_unordered(PNGScriptCrawl, triples, chunksize=num_p),total=len(triples)):
                res.append(x)
            pool.close()
            FileUtility.save_list(triples[0][1]+'log.txt',PNGScriptCrawl.log)


    @staticmethod
    def sequential_crawl(triples, override=False):

        if not override:
            new_list=[]
            for x,y,z in triples:
                if not FileUtility.exists(y+z):
                    new_list.append((x,y,z))
            triples=new_list

        print ('Start crawling..')
        for x in tqdm.tqdm(triples):
            PNGScriptCrawl(x)
        FileUtility.save_list(triples[0][1]+'log.txt',PNGScriptCrawl.log)

    def run_parser(self, basedir, outputfile):
        book2numbers = BibleParser.create_books2numbers(self)
        result = []
        for dirName, subdirList, fileList in os.walk(basedir):
            fileList.sort()
            for filename in fileList:
                if not filename.endswith('.htm'):
                    continue
                match = re.match('[0-9]*[A-Z]+', filename)
                if not match:
                    print('skipping unknown file', filename, file=sys.stderr)
                    continue
                bookname = match.group().lower()
                if bookname not in book2numbers:
                    print('skipping unknown file', filename, file=sys.stderr)
                    continue
                book_number = book2numbers[bookname]
                match = re.search(r'([0-9]+)\.htm', filename)
                if not match:
                    print('skipping unknown file', filename, file=sys.stderr)
                    continue
                chapter_number = match.group(1).zfill(3)
                if chapter_number == '000':
                    #print >> sys.stderr, 'skipping intro file', filename
                    continue
                verses = self.parse_chapter(os.path.join(dirName, filename))
                result.extend((book_number + chapter_number + str(i).zfill(3), v) for i, v in verses)
        result.sort()

        f = codecs.open(outputfile, 'w', 'utf-8')
        for i, v in result:
            f.write('%s\t%s\n' % (i, ' '.join(w for w in v.split(' ') if w)))
        f.close()

    def parse_chapter(self, filename):
        verses = []
        v_number = None
        state = None
        text = ''
        ignore = False

        #document = etree.parse(open(args[0]))
        document = lxml.html.parse(io.open(filename, encoding='utf8'))
        for event, element in etree.iterwalk(document, events=("start", "end")):
            if element.attrib.get('class', '') in ['it', 'notemark', 'rq', 's', 'd', 'r', 'sr']:
                #it, rq  italic
                #notemark  footnotemark
                #s centered header lines
                #q left aligned fat lines
                #r references below headings
                #sr dito
                ignore = event == 'start'

            if event == 'start' and element.tag == 'span' and element.attrib.get('class', '') == 'verse':
                if v_number:
                    verses.append((v_number, ' '.join(text.strip().split())))
                text = ''
                state = 'verse_number'
            elif event == 'end' and state == 'verse_number' and element.tag == 'span' and element.attrib.get('class', '') == 'verse':
                text += element.text
                v_number = text.strip()
                state = 'verse'
                text = ''
            elif event == 'start' and state == 'verse' and element.tag == 'ul':
                # last verse
                verses.append((v_number, ' '.join(text.strip().split())))
                state = None
            if state == 'verse' and not ignore:
                if event == 'start' and element.text:
                    text += element.text
                elif event == 'end' and element.tail:
                    text += element.tail

        result = []
        for num, text in verses:
            match = re.search(r'(\d+)\s*-\s*(\d+)', num)
            if match:
                result.append((match.group(1), text))
                for x in range(int(match.group(1))+1, int(match.group(2))+1):
                    result.append((str(x), ''))
            else:
                result.append((num, text))
        return result


if __name__ == '__main__':
    if requests.get("http://pngscriptures.org/robot.txt").status_code == 404:
        print ("No robot.txt found. Let's continue..")
    else:
        if query_yes_no("There is a robot.txt file at http://pngscriptures.org/robot.txt. Do you want to check manually your eligibility first?"):
            exit()
        else:
            print("OK, Let's continue..")
    triple=[(l.split()[1],'/mounts/data/proj/asgari/final_proj/000_datasets/testbib/pngscript_new/', l.split()[0]) for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/finalized_urls/pngscriptures.txt')]
    PNGScriptCrawl.parallel_crawl(triple,5)
