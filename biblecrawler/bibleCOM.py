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

class BibleCom(BibleCrawler,BibleParser):
    log=[]

    def __init__(self, triple, crawl=True, parse=True, remove_after_parse=False, printing=False):
        '''
        :param url:
        :param destination_directory:
        :param output_file:
        '''
        try:
            # get parameters
            self.url, self.destination_directory, output_file=triple
            self.output_file=self.destination_directory + output_file
            self.print=printing


            if not '.' in self.url.split('/')[-1]:
                self.url=self.url+'/MAT.1'

            print (self.url)
            if crawl:
                BibleCrawler.run_crawler(self,'//div[contains(@class, "next-arrow")]//@href',self.url, self.destination_directory, website='bible.com')
            if parse:
                self.url=self.url[self.url.find('.com')+5::]
                if '.' in self.url.split('/')[-1]:
                    self.lang_directory = '/'.join(self.url.split('/')[0:-1])+'/'
                print (self.lang_directory)
                print (self.destination_directory)
                print (books)
                books=self.destination_directory + self.lang_directory
                self.run_parser(books, self.output_file)
        except:
            try:
                print (triple)
            except:
                return None
        # parse the output file
        # remove the directory
        #FileUtility.remove_dir(self.destination_directory + self.lang_directory)
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
            new_list=[]
            for x,y,z in triples:
                if not FileUtility.exists(y+z):
                    new_list.append((x,y,z))
            triples=new_list
        if len(triples)>0:
            print ('Start parallel crawling..')
            pool = Pool(processes=num_p)
            res=[]
            for x in tqdm.tqdm(pool.imap_unordered(BibleCom, triples, chunksize=num_p),total=len(triples)):
                res.append(x)
            pool.close()
            FileUtility.save_list(triples[0][1]+'log.txt',BibleCom.log)


    @staticmethod
    def sequential_crawl(triples, override=False):
        '''
        :param triples:
        :param override:
        :return:
        '''
        if not override:
            new_list=[]
            for x,y,z in triples:
                if not FileUtility.exists(y+z):
                    new_list.append((x,y,z))
            triples=new_list

        print ('Start crawling..')
        for x in tqdm.tqdm(triples):
            BibleCom(x)
        FileUtility.save_list(triples[0][1]+'log.txt',BibleCom.log)

    def run_parser(self, basedir, outputfile):
        '''
        :param basedir:
        :param outputfile:
        :return:
        '''
        book2numbers = BibleParser.create_books2numbers(self)
        result = []

        for dirName, subdirList, fileList in os.walk(basedir):
            fileList.sort()
            for filename in fileList:
                match = re.match('\d*[a-zA-Z]', filename)
                if not match:
                    if self.print:
                        print('skipping unknown file', filename, file=sys.stderr)
                    BibleCom.log.append(' '.join(['skipping unknown file', filename]))
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
        '''
        :param filename:
        :return:
        '''
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
    if not requests.get("http://bible.com/robot.txt").status_code ==404:
        print ("No robot.txt found. Let's continue..")
    else:
        if query_yes_no("There is a robot.txt file at http://bible.com/robot.txt. Do you want to check manually your eligibility first?"):
            exit()
        else:
            print("OK, Let's continue..")

    triple=[(l.split()[1],'/mounts/data/proj/asgari/final_proj/000_datasets/testbib/biblecom_extra/', l.split()[0]) for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/extra_handled_bible.com.txt')]
    BibleCom.parallel_crawl(triple, num_p=20)
