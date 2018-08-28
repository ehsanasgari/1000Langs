#!/usr/bin/env python3

import sys
import os
import re
import io
import lxml.html
from lxml import etree

#pull book and chapter out of the filename
REGEX = re.compile(r'(\d+).*-(\d+)\.htm')

#multiline verses
VERSE_RANGE = re.compile(r'(\d+)\s*-\s*(\d+)')

def extend_text(text, new_text, open_tags):
    if new_text is None or 'a' in (x[0] for x in open_tags) \
       or [x for x in open_tags if x[0] == 'span' and 'verse' in x[1]] \
       or [x for x in open_tags if x[0] == 'div' and ('sectionheading' in x[1] or 'parallel' in x[1])]:
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

    parser = lxml.html.HTMLParser(encoding='utf8')
    document = lxml.html.parse(io.open(filename, 'rb'), parser)
    for event, element in etree.iterwalk(document, events=("start", "end")):
        if event == 'start':
            open_tags.append((element.tag, element.attrib.get('class', '')))
            text = extend_text(text, element.text, open_tags)
        if event == 'start' and element.tag == 'span' and element.attrib.get('class', '') == 'verse':
            append_verse(verses, v_number, range_end, text)
            if '-' in element.text:
                match = VERSE_RANGE.search(element.text)
                if not match:
                    print('skipping bogus verse number:', match.group(), file=sys.stderr)
                    v_number = None
                else:
                    v_number = int(match.group(1))
                    range_end = int(match.group(2))
            else:
                v_number = int(element.text.strip())
                range_end = v_number
            text = ''
        elif event == 'start' and element.tag == 'div' and 'navButtons' in element.attrib.get('class'):
            append_verse(verses, v_number, range_end, text)
            v_number = None
        if event == 'end':
            open_tags.pop()
            text = extend_text(text, element.tail, open_tags)
    return verses


def main(args):
    basedir = args[0]
    result = []
    for dirName, subdirList, fileList in os.walk(basedir):
        fileList.sort()
        for filename in fileList:
            match = REGEX.match(filename)
            if not match:
                print('skipping unknown file:', filename, file=sys.stderr)
                continue
            book_number = match.group(1).zfill(2)
            chapter_number = match.group(2).zfill(3)
            verses = parse_chapter(os.path.join(dirName, filename))
            result.append((book_number, chapter_number,
                           list((book_number + chapter_number + str(i).zfill(3), v) for i,v in verses)))
    result.sort()
    for _, _, verses in result:
        for i,v in verses:
            sys.stdout.write('%s\t%s\n' % (i,' '.join(v.split())))
                                   
    
if __name__ == '__main__':
    main(sys.argv[1:])
