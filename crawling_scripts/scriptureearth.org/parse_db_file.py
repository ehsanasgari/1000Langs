#!/usr/bin/env python3

import sys
import re
import unicodedata
import sqlite3

PATTERN = re.compile(r'(<(?P<tag>\w+)(?: [^>]+)?>).*?(<\s*/\s*(?P=tag)\s*>)')
def strip_tags(line):
    while True:
        match = PATTERN.search(line)
        if not match:
            break
        line = line[:match.start(0)] + \
               line[match.end(1):match.start(3)] + \
               line[match.end(3):]
    return line


def clean_verse(name, text):
    if text is None:
        return None, 0
    text = text.strip()
    while text.startswith('<TS'):
        #remove headings <TS1> or <TS3>
        end = text.find('<Ts>')
        if end == -1:
            print("%s: Invalid <TS1>..<ts>: %s" % (name, text[:40]), file=sys.stderr)
            break
        text = text[end+4:].lstrip()

    while True:
        #remove footnotes
        start = text.find('<RF')
        if start == -1:
            break
        end = text.find('<Rf>')
        if end == -1:
            print("%s: Invalid <Rf>..<Rf>: %s" % (name, text[:40]), file=sys.stderr)
            break
        text = text[:start] + text[end+4:]

    #expand multiverse entries i.e. <sup>(6-7)</sup>
    match = re.search(r'(?:<sup>)?\s*\(\s*([0-9]+)\s*-\s*([0-9]+)\s*\)\s*(?:</sup>)?\s*', text)
    if match:
        extra = int(match.group(2)) - int(match.group(1))
        text = text[match.end():]
    else:
        extra = 0

    #strip HTML matching tag pairs
    text = strip_tags(text)

    while True:
        # strip single tags
        match = re.search(r'\s*(<[\w\d]+>\s*)+', text)
        if match is None:
            break
        text = text[:match.start()] + ' ' + text[match.end():]


    text = unicodedata.normalize('NFC', text)
    text = text.strip()

    if not text or text == '(-)':
        text = None

    return text, extra


def main(args):
    conn = sqlite3.connect(args[0])
    result = conn.execute("""select * from "Bible" order by "Book", "Chapter", "Verse";""")
    for book, chapter, verse, text in result:
        name = '%02i%03i%03i' % (book, chapter, verse)
        text, extra = clean_verse(name, text)
        if text:
            print('%s\t%s' % (name, text))
            for index in range(extra):
                name = '%02i%03i%03i' % (book, chapter, verse+index+1)
                print('%s\t' % name)

if __name__ == '__main__':
    main(sys.argv[1:])
