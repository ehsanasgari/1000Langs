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
from biblecrawler.crawler_general import BibleCrawler
from biblecrawler.parser_general import BibleParser

class BibleISCrawl(BibleCrawler,BibleParser):
    SLEEPTIME = 4  # seconds
    log=[]

    def __init__(self, triple, print=False):
        '''
        :param url:
        :param destination_directory:
        :param output_file:
        '''
        # get parameters
        self.url, self.destination_directory, output_file=triple
        self.output_file=self.destination_directory + output_file
        self.print=print
        # find the lang ID in the website
        self.lang_directory = self.url.split('/')[3]
        # crawl the pages
        BibleCrawler.run_crawler(self,'//a[@class = "chapter-nav-right"]/@href',self.url, self.destination_directory)
        # parse the output file
        #books=self.destination_directory + self.lang_directory
        #self.run_parser(books, self.output_file )
        # remove the directory
        #FileUtility.remove_dir(self.destination_directory + self.lang_directory)
        return None

    @staticmethod
    def parallel_crawl(triples, num_p):
        print ('Start parallel crawling..')
        pool = Pool(processes=num_p)
        res=[]
        for x in tqdm.tqdm(pool.imap_unordered(BibleISCrawl, triples, chunksize=num_p),total=len(triples)):
            res.append(x)
        pool.close()
        FileUtility.save_list(triples[0][1]+'log.txt',BibleISCrawl.log)


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
            BibleISCrawl(x)
        FileUtility.save_list(triples[0][1]+'log.txt',BibleISCrawl.log)



if __name__ == '__main__':

    triple=[(l.split()[1],'/mounts/data/proj/asgari/final_proj/000_datasets/testbib/bibleis/', l.split()[0]) for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/handled_bible.is.txt')]
    BibleISCrawl.sequential_crawl([triple[1]])
