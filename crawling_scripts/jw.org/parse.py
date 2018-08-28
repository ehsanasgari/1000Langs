#!/usr/bin/env python3

import sys
import os
import io
from lxml import html, etree
import unicodedata

HEADER = """# language_name:        
# closest ISO 639-3:    
# year_short:           
# year_long:            Not available
# title:                <br>New World Translation of the Holy Bible in
# URL:                  http://www.jw.org/
# copyright_short:      © Watch Tower Bible and Tract Society of Pennsylvania
# copyright_long:       Not available"""


def parse(filename, seen_tags):
    verses = []
    open_tags = []

    verse_number = None

    text = ''

    parser = html.HTMLParser(encoding='utf8')
    document = html.parse(io.open(filename, 'rb'), parser)

    for event, element in etree.iterwalk(document, events=("start", "end")):
        if event == 'start':
            open_tags.append(element.tag)

            if verse_number is not None:
                seen_tags.add(element.tag)

            if element.tag == 'span' and 'verse' in element.attrib.get('class', ''):
                verse_number = element.attrib.get('id', '???')[1:] # id="v40001001" or id="v1001001"
                verse_number = verse_number.zfill(8)
            if verse_number is not None and element.text is not None \
               and 'sup' not in open_tags and 'a' not in open_tags:
                text += element.text

        elif event == 'end':
            if element.tag == 'span' and 'verse' in element.attrib.get('class', '') and verse_number is not None:
                text = text.strip()
                verses.append((verse_number, text))
                text = ''
                verse_number = None

            open_tags.pop()
            if verse_number is not None and element.tail is not None \
               and 'sup' not in open_tags and 'a' not in open_tags:
                text += element.tail
    return verses


def main(args):
    basedir = args[0]
    result = []

    seen_tags = set()
    for dirName, subdirList, fileList in os.walk(basedir):
        fileList.sort()
        for filename in fileList:
            result.extend(parse(os.path.join(dirName, filename), seen_tags))
    result.sort()

    print(sorted(seen_tags), file=sys.stderr)

    print(HEADER)
    for i, v in result:
        print('%s\t%s' % (i, unicodedata.normalize('NFC', ' '.join(v.split()))))


if __name__ == '__main__':
    main(sys.argv[1:])
