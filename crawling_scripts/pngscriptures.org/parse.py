#!/usr/bin/env python3

import sys
import os
import re
import io
import lxml.html
from lxml import etree


HEADER = """# language_name:
# closest ISO 639-3:    %s
# year_short:
# year_long:            Not available
# title:
# URL:                  http://pngscriptures.org/%s/
# copyright_short:
# copyright_long:       Not available
"""


def parse_chapter(filename):
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
    iso_code = args[2]

    book2numbers = create_books2numbers(book2numbers_filename)
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
            verses = parse_chapter(os.path.join(dirName, filename))
            result.extend((book_number + chapter_number + str(i).zfill(3), v) for i, v in verses)
    result.sort()

    sys.stdout.write(HEADER % (iso_code, iso_code))
    for i, v in result:
        sys.stdout.write('%s\t%s\n' % (i, ' '.join(w for w in v.split(' ') if w)))


if __name__ == '__main__':
    main(sys.argv[1:])
