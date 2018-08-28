The crawling script needs as starting point the URL to the first chapter
of the bible to be crawled because it simply follows the 'reader-next'
links to the following chapter to crawl the whole bible.

The parsing script can't cope with verses spanning multiple verse numbers.

It now works when downloading the sites without UTF-8 conversion, and only convert the encoding inside the parse.py script.

### old ideas

slight changes to the crawling script to find the right web addresses. Seems to work now

unicode encoding seems to make errors. Files I tried to save without utf-8 conversion, so some conversion has to be done afterwards, e.g. recode html download/* . However, that didn't seem to be the problem.

there is a problem with various space-characters (U+200B, U+200C, U+200D)
zero width spaces have to be removed, I tried something like this:

cd bible/174
for f in *; do tr -d $'\342\200\213\342\200\214\342\200\215' < $f > ../174_2/$f ; done

Only then parse!

however: there are still incomplete lines in the resulting file after parsing :-(.  Something prevents the right parsing, but I cannot find the problem.

parse.py bible/174 ../books2numbers.txt > 174.txt
parse.py bible/174_2 ../books2numbers.txt > 174_2.txt

The parsed version after removing the spaces is better, but there are still errors (compare with downloads, or with https://www.bible.com/hi/bible/174/gen.1). E.g.line 19 (01001019) is suddenly broken off, and also line 83 (01004015), and many more like this.