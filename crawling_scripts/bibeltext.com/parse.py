#!/usr/bin/env python3

import sys
import os
import io
import lxml.html
from lxml import etree


def parse_chapter(filename):
    verses = []
    v_number = None
    state = None
    text = ''

    #document = etree.parse(open(args[0]))
    document = lxml.html.parse(io.open(filename, encoding='utf8'))
    for event, element in etree.iterwalk(document, events=("start", "end")):
        if event == 'end' and state is not None and element.text is not None:
            text += element.text
        if event == 'start' and element.tag == 'span':
            state = element.attrib['class']
            text = ''
        elif event == 'end' and element.tag == 'span':
            if state == 'reftext':
                v_number = int(text.strip())
            elif state == 'maintext':
                verses.append((v_number, text))
            state = None
            text = None

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
                print("No tab separator in this line:")
                print(("\t" + book_entry))
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
        parts = os.path.split(dirName)
        if parts[-1].lower() not in book2numbers:
            print('skipping unknown directory', dirName, file=sys.stderr)
            continue
        book_number = book2numbers[parts[-1].lower()]
        for filename in fileList:
            print(filename, file=sys.stderr)
            chapter_number = filename[:filename.find('.')].zfill(3)
            verses = parse_chapter(os.path.join(dirName, filename))
            result.extend((book_number + chapter_number + str(i).zfill(3), v) for i, v in verses)
    result.sort()
    for i, v in result:
        print('%s\t%s' % (i, v))


if __name__ == '__main__':
    main(sys.argv[1:])
