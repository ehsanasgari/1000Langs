#!/usr/bin/env python3

import sys
import os
import re
import io
import lxml.html
import unicodedata
from lxml import etree

HEADER = """\
# language_name:        
# closest ISO 639-3:    
# year_short:           
# year_long:            Not available
# title:                
# URL:                  
# copyright_short:      
# copyright_long:       Not available
"""

#multiline verses (not used at myanmarbible.com, artifakt from copy/paste)
VERSE_RANGE = re.compile(r'(\d+)\s*-\s*(\d+)')

header_lines = {'h1', 'h2', 'h3', 'h4', 'h5'}

def extend_text(text, new_text, open_tags):
    if new_text is None or not [t for t in open_tags if t.tag == 'div' and t.attrib.get('class', '') == 'verses']:
        return text
    if header_lines.intersection(t.tag for t in open_tags) or\
       [t for t in open_tags if t.attrib.get('class', '') == 'footnote'] or\
       not ((open_tags[-1].tag == 'span' and open_tags[-1].attrib.get('onmouseover', '').startswith('setCurrentVerse'))\
            or open_tags[-1].tag == 'p' ):
        return text
    else:
        return text + new_text

    
def append_verse(verses, v_number, range_end, text):
    if v_number is not None:
        verses.append((v_number, text))
        for x in range(v_number +1, range_end + 1):
            verses.append((x, ''))

    
def parse_chapter(filename):
    verses = []
    v_number = None
    range_end = None
    text = ''
    open_tags = []

    verse_regex = re.compile(r'ch\d+v(\d+)')
    range_regex = re.compile(r'\d+:\d+-(\d+)')
    parser = lxml.html.HTMLParser(encoding='utf8')
    document = lxml.html.parse(io.open(filename, 'r', encoding='utf8', errors='ignore'), parser)
    for event, element in etree.iterwalk(document, events=("start", "end")):
        if event == 'start':
            open_tags.append(element)
            text = extend_text(text, element.text, open_tags)
        if event == 'start' and element.tag == 'span' and element.attrib.get('class', '') == 'verseId':
            append_verse(verses, v_number, range_end, text)
            match = verse_regex.match(element.attrib.get('id', ''))
            if not match:
                print(filename, 'skipping bogus verse number', element.attrib.get('id', ''), file=sys.stderr)
                v_number = None
                continue
            v_number_text = match.group(1)
            if '-' in v_number_text:
                match = VERSE_RANGE.search(v_number_text)
                if not match:
                    print(filename, 'skipping bogus verse number:', match.group(), file=sys.stderr)
                    v_number = None
                else:
                    v_number = int(match.group(1))
                    range_end = int(match.group(2))
            else:
                v_number = int(v_number_text)
                range_end = v_number
            text = ''
        elif event == 'start' and element.tag == 'span' and \
             element.attrib.get('onmouseover', '').startswith('setCurrentVerse'):
            match = range_regex.search(element.attrib['onmouseover'])
            if match:
                range_end = int(match.group(1))
        if event == 'end':
            if v_number and element.tag == 'div':
                append_verse(verses, v_number, range_end, text)
                v_number = None
            open_tags.pop()
            text = extend_text(text, element.tail, open_tags)
    return verses


def create_books2numbers(filename):
    """This method creates the book2numbers dictionary of (alternate) book
    names to numbers in the Par format.
    """

    books2numbers = dict()
    with io.open(filename, encoding="utf-8") as books_file:
        for book_entry in books_file:
            try:
                (book_number, book_names) = book_entry.strip().split("\t", 1)
            except ValueError:
                print("No tab separator in this line:", file=sys.stderr)
                print("\t" + book_entry, file=sys.stderr)
            for alt_name in book_names.split(","):
                alt_name = alt_name.lower()
                books2numbers[alt_name] = book_number
    return books2numbers


def main(args):
    basedir = args[0]
    book_names = args[1]
    books2numbers = create_books2numbers(book_names)
    result = []

    ch_regex = re.compile(r'(\d+)\.html')
    for dirName, subdirList, fileList in os.walk(basedir):
        parts = os.path.split(dirName)
        if parts[-1].lower() not in books2numbers:
            print('Skipping directory', dirName, file=sys.stderr)
            continue        
        book_number = str(books2numbers[parts[-1].lower()]).zfill(2)
        fileList.sort()
        for filename in fileList:
            match = ch_regex.search(filename)
            if not match:
                print('Skipping unknown file', filename, file=sys.stderr)
                continue
            chapter_number = match.group(1).zfill(3)
            #print(filename, file=sys.stderr)
            verses = parse_chapter(os.path.join(dirName, filename))
            result.append((book_number, chapter_number,
                           list((book_number + chapter_number + str(i).zfill(3), v) for i,v in verses)))
    result.sort()
    sys.stdout.write(HEADER)
    for book, chapter, verses in result:
        for i, v in verses:
            sys.stdout.write('%s\t%s\n' % (i, unicodedata.normalize('NFC', ' '.join(v.split()))))
                                   
    
if __name__ == '__main__':
    main(sys.argv[1:])
