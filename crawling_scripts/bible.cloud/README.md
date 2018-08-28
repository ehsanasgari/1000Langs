The crawling script needs as starting point the URL to the first chapter
of the bible to be crawled because it simply follows the link to the
following chapter to crawl the whole bible.

The parsing script expects the normal parameters `directory`,
`books2numbers file`

for example:

file=FUESIM
crawl.py http://bible.cloud/bible/content/texts/$file/MT1.html $file
parse.py $file ../books2numbers.txt > $file.txt
../../scripts/separate_punctuation.py $file.txt


file=WATWBT ; python3 crawl.py http://bible.cloud/bible/content/texts/$file/GN1.html $file ; python3 parse.py $file ../books2numbers.txt > $file.txt ; ../../scripts/separate_punctuation.py $file.txt