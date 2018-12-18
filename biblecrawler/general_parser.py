__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__website__ = "https://llp.berkeley.edu/asgari/"
__git__ = "https://github.com/ehsanasgari/"
__email__ = "ehsan.asgari@gmail.com"
__project__ = "1000Langs -- Super parallel project at CIS LMU"

#!/usr/bin/env python3

import sys
import os
import re
import io
import lxml.html
from lxml import etree
'''
This code is largely inspired/adapted from Michael Cysouw's crawling code
'''

class BibleParser(object):
    def __init__(self,filename):
        self.parser_create_books2numbers(filename)

    def create_books2numbers(self):
        """This method creates the book2numbers dictionary of (alternate) book
        names to numbers in the Par format.
        """

        books2numbers = dict()
        with io.open('../meta/books2numbers.txt', encoding="utf-8") as books_file:
            for book_entry in books_file:
                try:
                    (book_number, book_names) = book_entry.strip().split("\t", 1)
                except ValueError:
                    if self.print:
                        print("No tab separator in this line:", file=sys.stderr)
                        print("\t" + book_entry, file=sys.stderr)
                    continue
                for alt_name in book_names.split(","):
                    alt_name = alt_name.lower()
                    books2numbers[alt_name] = book_number
        return books2numbers

