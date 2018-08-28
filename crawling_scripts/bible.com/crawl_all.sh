#!/bin/bash

# for file in 1054 911 1063 154 417 1223 160 161 166 210 214 442 53 222 411 753 1076;

mkdir crawl
mkdir files

for file in 981 1291 1332 1333 ;

do
	mkdir crawl/$file
	python3 crawl.py https://www.bible.com/bible/$file/mat.1 crawl/$file
	python3 parse_new.py crawl/$file ../books2numbers.txt > files/$file.txt
	../../scripts/separate_punctuation.py files/$file.txt
done

for file in 1362 1430 1335 ;

do
	mkdir crawl/$file
	python3 crawl.py https://www.bible.com/bible/$file/gen.1 crawl/$file
	python3 parse_new.py crawl/$file ../books2numbers.txt > files/$file.txt
	../../scripts/separate_punctuation.py files/$file.txt
done

mv files ~/Desktop
mv crawl '/Users/cysouw/Documents/Github/Parallel Texts/'