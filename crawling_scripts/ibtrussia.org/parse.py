#!/usr/bin/env python3

import sys
import os
import re
import io
import lxml.html
from lxml import etree


def parse_chapter(filename):
    document = lxml.html.parse(io.open(filename, encoding='utf8'))

    num = document.xpath('//span[contains(@class,"vs ")]/attribute::title')
    num[:] = [s.split('.')[2] for s in num]
    sel = document.xpath('//span[contains(@class,"vs ")]')
    text = [a.xpath('normalize-space(.)') for a in sel]
    text[:] = [re.sub('^\d+ ','',s) for s in text]
    
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

def create_books2numbers(filename):
    """This method creates the book2numbers dictionary of (alternate) book
    names to numbers in the Par format.
    """
    books2numbers = dict()
    with open(filename, encoding="utf-8") as books_file:
        for book_entry in books_file:
            try:
                book_number, book_names = book_entry.strip().split("\t", 1)
            except ValueError:
                print("No tab separator in this line:", file=sys.stderr)
                print("\t" + book_entry, file=sys.stderr)
                continue
            for alt_name in book_names.split(","):
                alt_name = alt_name.lower()
                books2numbers[alt_name] = book_number
    return books2numbers

def main(args):
    basedir = args[0]
    book2numbers_filename = args[1]

    book2numbers = create_books2numbers(book2numbers_filename)
    result = []
    for dirName, subdirList, fileList in os.walk(basedir):
        fileList.sort()
        for filename in fileList:
#            if not filename.endswith('.html'):
#                #
#                continue
            match = re.match('\d*[A-Z]', filename)
            if not match:
                print('skipping unknown file', filename, file=sys.stderr)
                continue
            number = re.search('\.', filename)
            if not number:
                bookname = filename
                book_number = book2numbers[bookname.lower()]
                chapter_number = '001'
            else:
                bookname = filename.split('.')[0]
#            if bookname not in book2numbers:
#                print('skipping unknown file', filename, file=sys.stderr)
#                continue
                book_number = book2numbers[bookname.lower()]
#            match = re.search(r'^[A-Z][A-Z0-9]([0-9]+)\.html', filename)
#            if not match:
#                print('skipping unknown file', filename, file=sys.stderr)
#                continue
                chapter_number = filename.split('.')[1].zfill(3)
#            if chapter_number == '000':
                #print >> sys.stderr, 'skipping intro file', filename
#                continue
            verses = parse_chapter(os.path.join(basedir, filename))
            result.extend((book_number + chapter_number + str(i).zfill(3), v) for i, v in verses)
    result.sort()

#    sys.stdout.write(HEADER % basedir)
    for i, v in result:
        sys.stdout.write('%s\t%s\n' % (i,v))


if __name__ == '__main__':
    main(sys.argv[1:])
