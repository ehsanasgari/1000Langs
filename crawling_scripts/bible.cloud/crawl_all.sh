#!/bin/bash

mkdir crawl
mkdir files

for file in PAONAB ;

do
	mkdir crawl/$file
	python3 crawl.py http://bible.cloud/bible/content/texts/$file/MT1.html crawl/$file
	python3 parse.py crawl/$file ../books2numbers.txt > files/$file.txt
	../../scripts/separate_punctuation.py files/$file.txt
done

for file in LCMPNG ;

do
	mkdir crawl/$file
	python3 crawl.py http://bible.cloud/bible/content/texts/$file/GN1.html crawl/$file
	python3 parse.py crawl/$file ../books2numbers.txt > files/$file.txt
	../../scripts/separate_punctuation.py files/$file.txt
done