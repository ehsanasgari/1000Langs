#!/bin/bash

mkdir crawl
mkdir files

for file in DA1EST ;

do
	mkdir crawl/$file
	python3 crawl.py http://www.bible.is/$file/1Cor/1 crawl/$file
	python3 parse.py crawl/$file ../books2numbers.txt > files/$file.txt
	../../scripts/separate_punctuation.py files/$file.txt
done