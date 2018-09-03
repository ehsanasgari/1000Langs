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


class BibleIsCrawl(object):
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
        self.run_crawler(self.url, self.destination_directory)
        # parse the output file
        books=self.destination_directory + self.lang_directory
        self.run_parser(books, self.output_file )
        # remove the directory
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

        print ('Start parallel crawling..')
        pool = Pool(processes=num_p)
        res=[]
        for x in tqdm.tqdm(pool.imap_unordered(BibleIsCrawl, triples, chunksize=num_p),total=len(triples)):
            res.append(x)
        pool.close()
        FileUtility.save_list(triples[0][1]+'log.txt',BibleIsCrawl.log)

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
            BibleIsCrawl(x)
        FileUtility.save_list(triples[0][1]+'log.txt',BibleIsCrawl.log)

    def run_crawler(self, url, destination_directory):

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
                BibleIsCrawl.log.append('\t'.join([self.output_file, 'Break on seen url:', str(url)]))
                break
            seen.add(url)
            if self.print:
                print(url)
            response = session.get(url)
            if response.status_code != requests.codes.ok:
                if self.print:
                    print('Error', url, response.url, response.status_code, file=sys.stderr)
                    print(time.strftime('%H:%M:%S'), url, file=sys.stderr)
                BibleIsCrawl.log.append('\t'.join([self.output_file, 'Error', str(url), str(response.url), str(response.status_code)]))
                sys.exit(1)
            self.save_response(response, destination_directory)
            url = self.get_next_url(response)
            if not url or not url.startswith('http'):
                if self.print:
                    print('Break on invalid url:', url, file=sys.stderr)
                BibleIsCrawl.log.append('\t'.join([self.output_file, 'Break on invalid url:', str(url)]))
                break
            time.sleep(BibleIsCrawl.SLEEPTIME)
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
        xpath_result = list(set(tree.xpath('//a[@class = "chapter-nav-right"]/@href')))
        relevant = xpath_result[0] if len(xpath_result) == 1 else None
        if relevant:
            return urljoin(response.url, relevant)
        else:
            return None

    def parse_chapter(self, filename):
        '''
        parser functionalities
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

    def parser_create_books2numbers(self, filename):
        """This method creates the book2numbers dictionary of (alternate) book
        names to numbers in the Par format.
        """

        books2numbers = dict()
        with io.open(filename, encoding="utf-8") as books_file:
            for book_entry in books_file:
                try:
                    (book_number, book_names) = book_entry.strip().split("\t", 1)
                except ValueError:
                    if self.print:
                        print("No tab separator in this line:", file=sys.stderr)
                        print("\t" + book_entry, file=sys.stderr)
                    continue
                for alt_name in book_names.split(","):
                    alt_name = alt_name.lower()
                    books2numbers[alt_name] = book_number
        return books2numbers

    def run_parser(self, basedir, outputfile):
        '''
        :param basedir:
        :param book2numbers_filename:
        :return:
        '''
        book2numbers = self.parser_create_books2numbers(
            '/mounts/data/proj/asgari/final_proj/1000langs/data_config/books2numbers.txt')
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


if __name__ == '__main__':

    triple=[(l.split()[1],'/mounts/data/proj/asgari/final_proj/000_datasets/testbib/bibleis/', l.split()[0]) for l in FileUtility.load_list('/mounts/data/proj/asgari/final_proj/1000langs/config/handled_bible.is.txt')]
    BibleIsCrawl.sequential_crawl(triple)
