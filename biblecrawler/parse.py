#!/usr/bin/env python3

import sys
import os
import io
import lxml.html
from lxml import etree


def parse_chapter(filename):
    verses = []
    last_v_number = -1
    v_number = None
    prev_open_bracket = False
    state = None
    text = ''

    #document = etree.parse(open(args[0]))
    try:
        document = lxml.html.parse(io.open(filename, encoding='utf8'))
    except UnicodeDecodeError as e:
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
                    print('Appending consecutive double verse numbers:', filename, v_number, file=sys.stderr)
                else:
                    verses.append((v_number, text.strip()))
                last_v_number = v_number
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
        parts = os.path.split(dirName)
        if parts[-1].lower() not in book2numbers:
            print('skipping unknown directory', dirName, file=sys.stderr)
            continue
        book_number = book2numbers[parts[-1].lower()]
        for filename in fileList:
            chapter_number = filename.zfill(3)
            verses = parse_chapter(os.path.join(dirName, filename))
            result.extend((book_number + chapter_number + str(i).zfill(3), v) for i, v in verses)
    result.sort()
    for i, v in result:
        sys.stdout.write('%s\t%s\n' % (i, ' '.join(w for w in v.split(' ') if w)))


if __name__ == '__main__':
    main(sys.argv[1:])
