#!/bin/bash


for file in DA1EST ;

do
	#python3 bible_is.py http://www.bible.is/DESWBT/Matt/1 /mounts/data/proj/asgari/dissertation/git_repos/0biblefiles/des/
	python3 parse.py /mounts/data/proj/asgari/dissertation/git_repos/0biblefiles/des/DESWBT/ /mounts/data/proj/asgari/dissertation/git_repos/1000langs/crawling_scripts/books2numbers.txt > /mounts/data/proj/asgari/dissertation/git_repos/0biblefiles/des/des.txt
	/mounts/data/proj/asgari/dissertation/git_repos/1000langs/crawling_scripts/separate_punctuation.py /mounts/data/proj/asgari/dissertation/git_repos/0biblefiles/des/des.txt
done
