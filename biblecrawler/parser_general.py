#!/usr/bin/env python3

import sys
import os
import re
import io
import lxml.html
from lxml import etree


class BibleParser(object):
    def __init__(self,filename):
        self.parser_create_books2numbers(filename)

    def create_books2numbers(self):
        """This method creates the book2numbers dictionary of (alternate) book
        names to numbers in the Par format.
        """

        books2numbers = dict()
        with io.open('/mounts/data/proj/asgari/final_proj/1000langs/data_config/books2numbers.txt', encoding="utf-8") as books_file:
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
