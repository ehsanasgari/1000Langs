#!/usr/bin/env python3

import sys
import os
import re
import io
from lxml import html, etree

#pull book and chapter out of the filename
REGEX = re.compile(r'(\w+)\.(\d+)')

VERSE = re.compile(r'\d+')

#multiline verses
VERSE_RANGE = re.compile(r'(\d+)\s*-\s*(\d+)')

def extend_text(text, new_text, open_tags):
    if new_text is None or 'a' in (x[0] for x in open_tags) \
       or not [x for x in open_tags if x[0] == 'span' and 'content' in x[1]]:
        return text
    else:
        return text + new_text


def append_verse(verses, v_number_spec, text):
    if v_number_spec is None:
        return
    if isinstance(v_number_spec, int):
        v_number = v_number_spec
        v_number_range = None
    else:
        v_number = v_number_spec[0]
        v_number_range = v_number_spec[1]

    if len(verses) == 0:
        verses.append((v_number, text))
    else:
        last = verses[-1]
        if last[0] == v_number:
            verses.pop()
            verses.append((v_number, last[1] + ' ' + text))
            print('joining verses', last[1] + ' | ' + text, file=sys.stderr)
        else:
            verses.append((v_number, text))
    if v_number_range is not None:
        for run in range(v_number+1, v_number_range+1):
            verses.append((run, ''))

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


def parse_chapter(filename):
    verses = []
    v_number = None
    text = ''
    open_tags = []

    parser = html.HTMLParser(encoding='utf8')
    document = html.parse(io.open(filename, 'r', encoding='utf8', errors='replace'), parser)
    #document = html.parse(io.open(filename, 'rb'), parser)

    for event, element in etree.iterwalk(document, events=('start', 'end')):
        if event == 'start':
            open_tags.append((element.tag, element.attrib.get('class', '')))
            if element.tag == 'span' and element.attrib.get('class', '') == 'label' and \
               not [x for x in open_tags if x[0] == 'span' and 'note' in x[1]]:
                append_verse(verses, v_number, text)
                text = ''
                try:
                    v_number = int(element.text)
                except ValueError:
                    match = VERSE_RANGE.match(element.text)
                    if match:
                        #print('multi verse:', element.text, file=sys.stderr)
                        v_number = (int(match.group(1)), int(match.group(2)))
                    else:
                        print('Ignoring bogus verse number:', element.text, file=sys.stderr)
                        v_number = None
            if element.tag == 'td':
                text = extend_text(text, ' ', open_tags)
            text = extend_text(text, element.text, open_tags)
        elif event == 'end':
            if element.tag == 'div' and 'chapter' in element.attrib.get('class', ''):
                append_verse(verses, v_number, text)
                text = ''
            elif element.tag in ['div', 'td']:
                text += ' '

            open_tags.pop()
            text = extend_text(text, element.tail, open_tags)
    return verses


def main(args):
    basedir = args[0]
    book2numbers_filename = args[1]

    book2numbers = create_books2numbers(book2numbers_filename)
    result = []
    for dirName, subdirList, fileList in os.walk(basedir):
        fileList.sort()
        for filename in fileList:
            if 'intro' in filename:
                continue
            match = REGEX.match(filename)
            if not (match and match.group(1).lower() in book2numbers):
                print('skipping unknown file:', filename, file=sys.stderr)
                continue
            book_number = book2numbers[match.group(1).lower()].zfill(2)
            chapter_number = match.group(2).zfill(3)
            verses = parse_chapter(os.path.join(dirName, filename))
            result.append((book_number, chapter_number,
                           list((book_number + chapter_number + str(i).zfill(3), v)
                                for i, v in verses)))
    #sort book and chapter, but leave verses as found in the file
    result.sort()
    for _, _, verses in result:
        for i, v in verses:
            sys.stdout.write('%s\t%s\n' % (i, ' '.join(v.split())))


if __name__ == '__main__':
    main(sys.argv[1:])
