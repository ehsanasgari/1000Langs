#!/bin/bash

file=$1
start=$2

mkdir crawl
mkdir files

python3 crawl.py https://www.bible.com/bible/$file/$start crawl/$file
python3 parse_new.py crawl/$file ../books2numbers.txt > files/$file.txt
../../scripts/separate_punctuation.py files/$file.txt

terminal-notifier -message "The text $file from bible.com is ready!"
