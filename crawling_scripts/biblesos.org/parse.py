#!/usr/bin/env python2

import sys
import os
import re
import io
import lxml.html
from lxml import etree


def parse_chapter(filename):
    verses = []
    v_number = None

    try:
        document = lxml.html.parse(io.open(filename, encoding='utf8'))
    except UnicodeDecodeError, e:
        print >> sys.stderr, filename, '\n', e
        document = lxml.html.parse(io.open(filename, encoding='utf8', errors='replace'))
    for event, element in etree.iterwalk(document, events=("start", "end")):
        if event == 'end' and element.tag == 'a':
            if not element.text or '.' not in element.text:
                continue
            v_number = element.text[element.text.index('.')+1:]
        elif event == 'end' and element.tag == 'span' and v_number is not None:
            verses.append((v_number, element.text.strip()))
        elif event == 'end' and element.tag == 'p':
            v_number = None
    return verses


def main(args):
    basedir = args[0]
    result = []
    for dirName, subdirList, fileList in os.walk(basedir):
        for filename in fileList:
            match = re.search('-\d*(\d{5})\d{6}.html', filename)
            if not match:
                print >> sys.stderr, 'Ignoring', filename
                continue
            
            book_chapter_number = match.group(1)
            verses = parse_chapter(os.path.join(dirName, filename))
            result.extend((book_chapter_number + str(i).zfill(3), v) for i,v in verses)
    result.sort()
    for i,v in result:
        print ('%s\t%s' % (i,v)).encode('utf8')
                                   
    
if __name__ == '__main__':
    main(sys.argv[1:])
