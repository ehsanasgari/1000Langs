#!/usr/bin/env bash

for i in crawl/* ;
do
#	echo out/${i#'crawl/'}.txt
	parse.py $i/bi12 > out/${i#'crawl/'}_bi12.txt
	separate_punctuation.py out/${i#'crawl/'}_bi12.txt ;
done