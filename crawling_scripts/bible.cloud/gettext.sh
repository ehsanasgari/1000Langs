#!/bin/bash

file=$1
start=$2

mkdir crawl
mkdir files

python3 crawl.py http://bible.cloud/bible/content/texts/$file/$start crawl/$file ;
python3 parse.py crawl/$file ../books2numbers.txt > files/$file.t
../../scripts/separate_punctuation.py files/$file.txt

terminal-notifier -message 'Text from bible.cloud is ready'