#!/usr/bin/env python3

import sys
import os
import re
import io
import lxml.html
from lxml import etree


#multiline verses (not used at alkitab.mobi, artifakt from copy/paste)
VERSE_RANGE = re.compile(r'(\d+)\s*-\s*(\d+)')


def extend_text(text, new_text, open_tags):
    if new_text is None or open_tags[-1].tag != 'p':
        return text
    else:
        return text + new_text

    
def append_verse(verses, v_number, range_end, text):
#    print(v_number, text, file=sys.stderr)
    if v_number is not None:
        verses.append((v_number, text))
        for x in range(v_number +1, range_end + 1):
            verses.append((x, ''))

    
def parse_chapter(filename):
#    print(filename, file=sys.stderr)
    verses = []
    v_number = None
    range_end = None
    text = ''
    open_tags = []

    parser = lxml.html.HTMLParser(encoding='utf8')
    document = lxml.html.parse(io.open(filename, 'r', encoding='utf8', errors='ignore'), parser)
    for event, element in etree.iterwalk(document, events=("start", "end")):
#        if filename == 'java2/jawa2/Kej/25.html':
#            print(event, element.tag, element.attrib, file=sys.stderr)
        if event == 'start':
            open_tags.append(element)
            text = extend_text(text, element.text, open_tags)
        if event == 'start' and element.tag == 'span' and element.attrib.get('class', '') == 'reftext':
#            print(element.text_content().strip(), file=sys.stderr)
            append_verse(verses, v_number, range_end, text)
            v_number_text = element.text_content().strip()
            if '-' in v_number_text:
                match = VERSE_RANGE.search(v_number_text)
                if not match:
                    print('skipping bogus verse number:', match.group(), file=sys.stderr)
                    v_number = None
                else:
                    v_number = int(match.group(1))
                    range_end = int(match.group(2))
            else:
                v_number = int(v_number_text)
                range_end = v_number
            text = ''
        if event == 'end':
            if v_number and element.tag == 'p':
                append_verse(verses, v_number, range_end, text)
                v_number = None
            open_tags.pop()
            text = extend_text(text, element.tail, open_tags)
    return verses


def get_b2n(filename):
    result = {}
    with open(filename) as f:
        for num, line in enumerate(f):
            result[line.strip()] = num+1
    return result


def fix_verse_numbering(book, verses):
    v_number = re.compile(r'\s*\((\d+)-(\d+)\)\s*')
    new_verses = []
    for i, verse in verses:
        match = v_number.search(verse)
        if not match:
            new_verses.append((i, verse))
            continue
        if match.start() != 0:
            new_verses.append((i, verse[:match.start()]))
        while True:
            match2 = v_number.search(verse, match.end())
            computed_v_number = book + match.group(1).zfill(3) + match.group(2).zfill(3)
            if not match2:
                new_verses.append((computed_v_number, verse[match.end():]))
                break
            else:
                new_verses.append((computed_v_number, verse[match.end():match2.start()]))
                match = match2
    return new_verses


def main(args):
    basedir = args[0]
    book_list = args[1]
    books2numbers = get_b2n(book_list)
    result = []
    for dirName, subdirList, fileList in os.walk(basedir):
        parts = os.path.split(dirName)
        if parts[-1] not in books2numbers:
            print('Skipping directory', dirName, file=sys.stderr)
            continue        
        book_number = str(books2numbers[parts[-1]]).zfill(2)
        fileList.sort()
        for filename in fileList:
            chapter_number = filename.split('.')[0].zfill(3)
            verses = parse_chapter(os.path.join(dirName, filename))
            result.append((book_number, chapter_number,
                           list((book_number + chapter_number + str(i).zfill(3), v) for i,v in verses)))
    result.sort()
    multiline = re.compile(r'\(\d+:\d+(-\d+)?\)\s*')
    for book, chapter, verses in result:
        verses = fix_verse_numbering(book, verses)
        for i, v in verses:
            match = multiline.match(v)
            if match:
                v = v[match.end():]
            sys.stdout.write('%s\t%s\n' % (i,' '.join(v.split())))
                                   
    
if __name__ == '__main__':
    main(sys.argv[1:])
