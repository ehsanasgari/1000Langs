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

class BibleComCrawl(BibleCrawler,BibleParser):
    '''
    Crawler for bible.cloud website
    '''
    log = []
    def __init__(self, triple, crawl=True, parse=True, remove_after_parse=False, printing=False):
        '''
        :param triple:
        :param crawl:
        :param parse:
        :param remove_after_parse:
        :param printing:
        '''
        try:
            # get parameters
            self.url, self.destination_directory, output_file=triple
            self.output_file=self.destination_directory + output_file
            self.print=printing

            if crawl:
                BibleCrawler.run_crawler(self,'//div[contains(@class, "next-arrow")]//@href',self.url, self.destination_directory, website='bible.org')

            if parse:
                self.url=self.url[self.url.find('.com')+5::]
                if '.' in self.url.split('/')[-1]:
                    self.lang_directory = '/'.join(self.url.split('/')[0:-1])+'/'
                books=self.destination_directory + self.lang_directory
                self.run_parser(books, self.output_file)
                if remove_after_parse:
                    # parse the output file
                    # remove the directory
                    FileUtility.remove_dir(self.destination_directory + self.lang_directory)
        except:
            try:
                print (triple)
            except:
                return None
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
            for x in tqdm.tqdm(pool.imap_unordered(BibleComCrawl, triples, chunksize=num_p),total=len(triples)):
                res.append(x)
            pool.close()
            FileUtility.save_list(triples[0][1]+'log.txt',BibleComCrawl.log)


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
            BibleComCrawl(x)
        FileUtility.save_list(triples[0][1]+'log.txt',BibleComCrawl.log)

    def run_parser(self, basedir, outputfile):
        book2numbers = BibleParser.create_books2numbers(self)
        result = []

        for dirName, subdirList, fileList in os.walk(basedir):
            fileList.sort()
            for filename in fileList:
                match = re.match('\d*[a-zA-Z]', filename)
                if not match:
                    if self.print:
                        print('skipping unknown file', filename, file=sys.stderr)
                    BibleCloud.log.append(' '.join(['skipping unknown file', filename]))
                    continue
                number = re.search('\.', filename)
                if not number:
                    bookname = filename
                    book_number = book2numbers[bookname.lower()]
                    chapter_number = '001'
                else:
                    bookname = filename.split('.')[0]

                    book_number = book2numbers[bookname.lower()]
                    chapter_number = filename.split('.')[1].zfill(3)
                verses = self.parse_chapter(os.path.join(dirName, filename))
                result.extend((book_number + chapter_number + str(i).zfill(3), v) for i, v in verses)
        result.sort()

        f = codecs.open(outputfile, 'w', 'utf-8')
        for i, v in result:
            f.write('%s\t%s\n' % (i, ' '.join(w for w in v.split(' ') if w)))
        f.close()


    def parse_chapter(self,filename):
        document = lxml.html.parse(io.open(filename, encoding='utf8'))

        for footnote in document.xpath('//span[contains(@class, "note f")]'):
            footnote.getparent().remove(footnote)

        num = document.xpath('//span[contains(@class,"verse ")]/attribute::class')
        num[:] = [re.sub(' v',' ', s) for s in num]
        num[:] = [re.sub(',',' ', s) for s in num]
        num[:] = [s.replace("verse ", "") for s in num]

        sel = document.xpath('//span[contains(@class,"verse ")]')
        text = [a.xpath('normalize-space(.)') for a in sel]
        text[:] = [re.sub('^[\d\-,]+','', s) for s in text]
        text[:] = [re.sub('^ ','', s) for s in text]

        num2 = []
        text2 = []
        # multiple verse numbers
        for n, t in zip(num, text):
            if ' ' in n:
                num2 += re.split(' ', n)
                text2 += [t]
                times = n.count(' ')
                text2 += ['']*times
            else:
                num2 += [n]
                text2 += [t]
        # repeating verse numbers
        num3 = []
        text3 = []
        unique = set(num2)
        for u in unique:
            num3 += [u]
            text3 += [' '.join([y for x,y in zip(num2,text2) if x==u])]

        text3[:] = [re.sub('^ +','', s) for s in text3]

        result = zip(num3, text3)
        return result


if __name__ == '__main__':

    triple=[(l.split()[1],'/mounts/data/proj/asgari/final_proj/000_datasets/testbib/biblecom/', l.split()[0]) for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/handled_bible.com.txt')]
    BibleComCrawl.parallel_crawl(triple,10)
