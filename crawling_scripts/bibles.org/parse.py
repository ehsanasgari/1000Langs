#!/usr/bin/env python3

import sys
import os
import re
import lxml.html
from lxml import etree


REGEX = re.compile(r'(\d+)\s*-\s*(\d+)')
TAGS_TO_SKIP = set(['sup', 'h3', 'h5', 'a'])


def extend_text(text, new_text, open_tags):
    if new_text is None or TAGS_TO_SKIP.intersection(t[0] for t in open_tags) \
       or [t for t in open_tags if t[0] == 'p' and 'rem' in t[1]]:
        return text
    else:
        return text + new_text


def append_verse(verses, v_number, v_number_part, text, pending):
    if v_number is None:
        return
    pre_v_number, pre_text = verses[-1] if verses else (None, None)
    if v_number_part is not None:
        print('Processing part %s, %s' % (pre_v_number, (v_number, v_number_part)), file=sys.stderr)
    if pre_v_number == v_number:
        verses.pop()
        verses.append((v_number, pre_text + ' ' + text))
    else:
        verses.append((v_number, text))
    if pending:
        for x in pending:
            verses.append((x, ''))


def parse_chapter(filename):
    verses = []
    v_number = None
    v_number_part = None
    pending = []
    text = ''
    open_tags = []

    #set encoding for the parser, because i only feed HTML fragments to the parser
    #and it can't determine the right encoding by itself
    parser = lxml.html.HTMLParser(encoding='utf8')
    document = lxml.html.parse(open(filename, 'rb'), parser)
    for event, element in etree.iterwalk(document, events=("start", "end")):
        if event == 'start':
            open_tags.append((element.tag, element.attrib.get('class', '')))
            text = extend_text(text, element.text, open_tags)
        else: # 'end'
            if element.tag == 'sup':
                append_verse(verses, v_number, v_number_part, text, pending)
                pending = []
                try:
                    v_number_str = element.text.strip()
                    # handle 17a, 17b etc
                    if v_number_str[-1].isalpha():
                        letter = v_number_str[-1]
                        if letter != 'a' and v_number_part is None or\
                           letter != 'a' and int(v_number_str[:-1]) != v_number or\
                           v_number_part is not None and ord(letter) != ord(v_number_part) + 1:
                            raise ValueError('Inconsistent Verse numbers: %s, %s, %s' %
                                             (v_number, v_number_part, v_number_str))
                        else:
                            v_number_part = v_number_str[-1]
                            v_number_str = v_number_str[:-1]

                    else:
                        v_number_part = None
                    # handle 10-12 etc
                    if '-' in  v_number_str:
                        match = REGEX.search(v_number_str)
                        if match:
                            v_number = int(match.group(1))
                            range_end = int(match.group(2))
                            pending = range(v_number+1, range_end+1)
                        else:
                            print(filename, v_number_str, file=sys.stderr)
                    else:
                        v_number = int(v_number_str)
                except ValueError as e:
                    print(filename, 'Ignoring fishy verse number', e, file=sys.stderr)
                    v_number = None
                    v_number_part = None
                except AttributeError as e:
                    print(filename, 'No verse number text found', e, open_tags, file=sys.stderr)
                    v_number = None
                    v_number_part = None
                    #raise e
                text = ''
            elif element.tag == 'div':
                append_verse(verses, v_number, v_number_part, text, pending)
                v_number = None
                v_number_part = None
                pending = []

            open_tags.pop()
            text = extend_text(text, element.tail, open_tags)
    return verses


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
            if not filename.endswith('.html'):
                continue
            parts = filename.split('.')
            if parts[0].lower() not in book2numbers:
                print('skipping unknown file:', filename, file=sys.stderr)
                continue
            book_number = book2numbers[parts[0].lower()]
            chapter_number = parts[1].zfill(3)
            verses = parse_chapter(os.path.join(dirName, filename))
            result.append((book_number, chapter_number,
                           list((book_number + chapter_number + str(i).zfill(3), v) for i, v in verses)))
    result.sort()
    for _, _, verses in result:
        for i, v in verses:
            sys.stdout.write('%s\t%s\n' % (i, ' '.join(w for w in v.split(' ') if w)))


if __name__ == '__main__':
    main(sys.argv[1:])
