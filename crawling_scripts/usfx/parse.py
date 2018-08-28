#!/usr/bin/env python3

import sys
import io
import lxml.html
from lxml import etree

HEADER = """\
# language_name:
# closest ISO 639-3:
# year_short:
# year_long:
# title:
# URL:
# copyright_short:      ©
# copyright_long:       """


#ignore footnote, figure, reference, section heading, crossref
ignore_text = lambda tags: set(['f', 'fig', 'ref', 's', 'x']).intersection(t[0] for t in tags)

#ignore section reference (comes directly after section header <s>)
#and rightaligned text
section_reference = lambda tags: [t for t in tags if t[0] == 'p' and t[1].get('sfm', '') in ['sr', 'r']]


def append_text(text, new_text, open_tags, seen):
    if ignore_text(open_tags) or section_reference(open_tags):
        return
    seen.add(open_tags[-1][0])
    text.append(new_text)


def parse(filename, books2numbers):
    verses = []
    v_prefix = None
    v_number = None
    v_end = None
    text = []
    open_tags = []
    seen = set()
    #document = etree.parse(open(args[0]))
    document = lxml.html.parse(io.open(filename, encoding='utf8'))
    for event, element in etree.iterwalk(document, events=("start", "end")):
        if event == 'start':
            if element.tag == 'v':
                b, c, v = element.attrib['bcv'].split('.')
                if b.lower() not in books2numbers:
                    print('Skipping unknown Book:', b, file=sys.stderr)
                else:
                    if '-' in v:
                        v_number, v_end = [int(x) for x in v.split('-')]
                    else:
                        v_number = int(v)
                        v_end = v_number
                    book = str(books2numbers[b.lower()])
                    v_prefix = '%s%s' % (book.zfill(2), c.zfill(3))
            elif element.tag == 've':
                verses.append(('%s%03i' % (v_prefix, v_number), ' '.join(text)))
                for run in range(v_number+1, v_end+1):
                    verses.append(('%s%03i' % (v_prefix, run), ''))
                text = []
                v_number = None
            open_tags.append((element.tag, element.attrib))
            if v_number and element.tag in ['p', 'q', 'th', 'tc']:
                #add space at start of paragraph and poetic lines and table headings/cells
                append_text(text, ' ', open_tags, seen)
            if v_number and element.text:
                append_text(text, element.text, open_tags, seen)
        elif event == 'end':
            open_tags.pop()
            if v_number and element.tail:
                append_text(text, element.tail, open_tags, seen)
    print('Tags stripped, text included for: ', sorted(seen), file=sys.stderr)
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
                print("No tab separator in this line:")
                print(("\t" + book_entry))
            for alt_name in book_names.split(","):
                alt_name = alt_name.lower()
                books2numbers[alt_name] = book_number
    return books2numbers


def main(args):
    filename = args[0]
    book2numbers_filename = args[1]

    book2numbers = create_books2numbers(book2numbers_filename)
    result = parse(filename, book2numbers)
    #result.sort()
    print(HEADER)
    for i, v in result:
        print('%s\t%s' % (i, ' '.join(w for w in v.split(' ') if w)))


if __name__ == '__main__':
    main(sys.argv[1:])
