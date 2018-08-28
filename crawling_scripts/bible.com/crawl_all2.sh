#!/bin/bash

# for file in 1054 911 1063 154 417 1223 160 161 166 210 214 442 53 222 411 753 1076;


for file in 470 473 ;

do
	mkdir crawl/$file
	python3 crawl.py https://www.bible.com/de/bible/$file/MAT.1 crawl/$file
	python3 parse_new.py crawl/$file ../books2numbers.txt > files/$file.txt
	../../scripts/separate_punctuation.py files/$file.txt
done

