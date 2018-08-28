#!/usr/bin/env python3

import sys
import re
from lxml import etree

CHAPTER_REGEX = re.compile(r'([0-9]+)\.?')
VERSE_REGEX = re.compile(r'\s*[0-9]+')

def parse(filename):

    verses = []
    book_number = 0
    chapter_number = 9999
    verse_number = 0
    parse_as_chapter = False
    text = []

    document = etree.parse(open(filename))
    #document = lxml.html.parse(io.open(filename, encoding='utf8'))
    for event, element in etree.iterwalk(document, events=("start", "end")):
        if event == 'start' and element.tag == 'text':
            if element.attrib.get('font', '') == '2' and \
               (element.text in ['DE PROFEET OBADJA.', 'FILÉMON.', 'JUDAS.'] or \
                (book_number in [62, 63] and element.text == 'JOHANNES.')):
                verse_id = '%02i%03i%03i' % (book_number, chapter_number, verse_number)
                verses.append((id, ' '.join(text)))
                text = []
                book_number += 1
                chapter_number = 1
            elif element.text and (element.text.startswith('HAEDSTIK') and element.attrib.get('font', '') == '3' \
               or element.text.startswith('SALM') and element.attrib.get('font', '') == '4'):
                print(element.text, file=sys.stderr)
                match = CHAPTER_REGEX.search(element.text)
                if match:
                    if book_number and text:
                        verse_id = '%02i%03i%03i' % (book_number, chapter_number, verse_number)
                        verses.append((verse_id, ' '.join(text)))
                        text = []
                    chapter_number = int(match.group(1))
                    if chapter_number == 1:
                        book_number += 1
                else:
                    parse_as_chapter = True
            elif parse_as_chapter and element.attrib.get('font', '') == '3':
                print(element.text, file=sys.stderr)
                if book_number and text:
                    verse_id = '%02i%03i%03i' % (book_number, chapter_number, verse_number)
                    verses.append((verse_id, ' '.join(text)))
                    text = []
                match = CHAPTER_REGEX.search(element.text)
                if match:
                    chapter_number = int(match.group(1))
                    if chapter_number == 1:
                        book_number += 1
                    parse_as_chapter = False
            elif element.attrib.get('font', '') == '3':
                match = VERSE_REGEX.match(element.text)
                if match:
                    if text:
                        verse_id = '%02i%03i%03i' % (book_number, chapter_number, verse_number)
                        verses.append((verse_id, ' '.join(text)))
                        text = [element.text[match.end():]]
                    verse_number = int(match.group())
                else:
                    text.append(element.text)
        elif event == 'end':
            if element.tag == 'pdf2xml':
                verse_id = '%02i%03i%03i' % (book_number, chapter_number, verse_number)
                verses.append((verse_id, ' '.join(text)))
    return verses


def main(args):
    filename = args[0]
    result = parse(filename)

    for i, v in result:
        try:
            print('%s\t%s' % (i, ' '.join(w for w in v.split(' ') if w)))
        except AttributeError:
            print((i, v), file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1:])
