#!/bin/bash

for file in NOG ;

do
	mkdir crawl/$file
	python3 crawl.py https://ibtrussia.org/en/text?m=$file crawl/$file ; 
	python3 parse.py crawl/$file ../books2numbers.txt > files/$file.txt ;
	../../scripts/separate_punctuation.py files/$file.txt
done

