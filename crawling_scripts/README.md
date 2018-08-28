## crawling and parsing scripts for Bibles

For every differnt source there is a directory which contains the different
scripts which crawl the source for a bible and in a second step parse the
downloaded data and extract the bible verses.

The scripts are written in python and require the following two additional
libraries:

- [requests](http://docs.python-requests.org/en/latest/user/install/#install) as a HTTP client library
- [lxml](http://lxml.de/installation.html) to parse HTML and XML data

The crawling scripts are designed to crawl a single Bible. To crawl all bibles on a site
additional code would be neccessary. Crawling scripts are called with two arguments:
First an URL which serves as an entry point to the desired bible and second
a directory where the pages will be saved. Sometimes instead of an URL some kind of
identifier is sufficient. See the site specific README.md for details.
 
The parsing script usually needs a mapping to correctly determine the book number.
This mapping is kept in the file `books2numbers.txt`. This directory contains a mapping,
which is suitable for most cases. Sometimes a special mapping is required which resides
in the same directory as the parsing script. Every script expects the mapping file as the
second command line argument after the directory which contains the files to parse (or the
filename, if the whole bible is in one file).
