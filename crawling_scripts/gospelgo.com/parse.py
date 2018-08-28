#!/usr/bin/env python3

import sys
import re
import io
import lxml.html
import unicodedata
from lxml import etree


VERSE_REGEX = re.compile(r'(^|\s+)[0-9]+\s+')
CHAPTER_REGEX = re.compile(r'[0-9]+$')
TAGS_TO_SKIP = set(['a'])


def extend_text(text, new_text, open_tags):
    if new_text is None or TAGS_TO_SKIP.intersection(t[0] for t in open_tags) \
       or [t for t in open_tags if t[0] == 'p' and 'blue' in t[1]]:
        pass
    else:
        text.append(new_text)


def parse_chapter(text):
    text = ''.join(text)
#    print(text)
    result = []
    matches = list((int(match.group()), match) for match in VERSE_REGEX.finditer(text))
#    print('---', len(matches))
    for run in range(len(matches)-1):
        result.append((matches[run][0], text[matches[run][1].end():matches[run+1][1].start()].strip()))
    result.append((matches[-1][0], text[matches[-1][1].end():].strip()))
    return result


def parse(filename):
    verses = []
    open_tags = []
    bookname = None
    booknumber = 39
    chapternumber = None
    text = []

    document = lxml.html.parse(io.open(filename, 'rb'))
    for event, element in etree.iterwalk(document, events=("start", "end")):
        if event == 'start':
            open_tags.append((element.tag, element.attrib.get('class', '')))
            extend_text(text, element.text, open_tags)

            if element.tag == 'a':
                if element.text is not None:
                    match = CHAPTER_REGEX.search(element.text)
                    if not match:
                        print('Ignoring anchor without chapter number', file=sys.stderr)
                    else:
                        if chapternumber:
                            pre = str(booknumber).zfill(2) + str(chapternumber).zfill(3)
                            verses.extend((pre+str(num).zfill(3), verse) for (num, verse) in parse_chapter(text))
                            text = []
                        print(element.text, file=sys.stderr)
                        name = element.text[:match.start()].strip()
                        chapternumber = int(match.group())
                        if name != bookname:
                            bookname = name
                            booknumber += 1
                            print('Increasing booknumber: %s = %i' % (name, booknumber), file=sys.stderr)
                else:
                    bookname = None

        else: # 'end'
            if element.tag == 'body':
                pre = str(booknumber).zfill(2) + str(chapternumber).zfill(3)
                verses.extend((pre+str(num).zfill(3), verse) for (num, verse) in parse_chapter(text))
                text = []
            open_tags.pop()
            extend_text(text, element.tail, open_tags)

    if booknumber != 66:
        print('Increasing booknumber: %s = %i' % (name, booknumber), file=sys.stderr)
    return verses


def main(args):
    filename = args[0]
    result = parse(filename)
    for i, v in result:
        sys.stdout.write('%s\t%s\n' % (i, unicodedata.normalize('NFC', ' '.join(v.split()))))


if __name__ == '__main__':
    main(sys.argv[1:])
