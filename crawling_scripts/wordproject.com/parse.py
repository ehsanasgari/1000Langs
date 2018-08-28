#!/usr/bin/env python3

import sys
import os
import re
import io
import lxml.html
from lxml import etree


#multiline verses
VERSE_RANGE = re.compile(r'(\d+)\s*-\s*(\d+)')

def extend_text(text, new_text, open_tags):
    if new_text is None or open_tags[-1].tag != 'p':
        return text    
    else:
        return text + new_text

    
def append_verse(verses, v_number, range_end, text):
    if v_number is not None:
        verses.append((v_number, text))
        for x in range(v_number +1, range_end + 1):
            verses.append((x, ''))

def node_text(node):
    if node.text:
        result = node.text
    else:
        result = ''
    for child in node:
        if child.tail is not None:
            result += child.tail
    return result

    
def parse_chapter(filename):
    verses = []
    v_number = None
    range_end = None
    text = ''
    open_tags = []

    parser = lxml.html.HTMLParser(encoding='utf-8')
    document = lxml.html.parse(io.open(filename, 'r', encoding='utf-8', errors='replace'), parser)
    #document = lxml.html.parse(io.open(filename, 'rb'), parser)

    for event, element in etree.iterwalk(document, events=("start", "end")):
        if event == 'start':
            open_tags.append(element)
            tmp=element.text
            #tmp=element.xpath("string()")
            #tmp=element.tostring(span)
            #tmp = node_text(element)
            #tmp = element.text_content()
            #tmp = ''.join(element.itertext())
            #tmp = etree.strip_tags(element, 'span')
            #tmp = etree.tostring(tmp)
            text = extend_text(text, tmp , open_tags)
        if event == 'start' and element.tag == 'span' and element.attrib.get('class', '') == 'verse':
            append_verse(verses, v_number, range_end, text)
            if '-' in element.text:
                match = VERSE_RANGE.search(element.text)#.text or .content
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
        if event == 'end':
            if v_number and element.tag == 'p':
                append_verse(verses, v_number, range_end, text)
                v_number = None
            open_tags.pop()
            #tmp = etree.tostring(element.tail, method = 'text')
            #tmp = element.xpath("//text()")
            #tmp = etree.tostring(element.tail) if element.tail else None
            tmp = element.tail
            text = extend_text(text, tmp, open_tags)
    return verses


def main(args):
    basedir = args[0]
    result = []
    for dirName, subdirList, fileList in os.walk(basedir):
        parts = os.path.split(dirName)
        book_number = parts[-1].zfill(2)
        fileList.sort()
        for filename in fileList:
            chapter_number = filename.split('.')[0].zfill(3)
            verses = parse_chapter(os.path.join(dirName, filename))
            result.append((book_number, chapter_number,
                           list((book_number + chapter_number + str(i).zfill(3), v) for i,v in verses)))
    result.sort()
    for _, _, verses in result:
        for i,v in verses:
            sys.stdout.write('%s\t%s\n' % (i,' '.join(v.split())))
                                   
    
if __name__ == '__main__':
    main(sys.argv[1:])
