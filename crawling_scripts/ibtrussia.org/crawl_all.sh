#!/bin/bash

for file in ADG AGL ALT AVR AZE BSK BEZ BUR CHE CHK CHV CRT DRG DNG GGZL GGZLCB GGZC GGZCCB GRG KBD KRKL KRK KAZ XKS KUM KYLSC KYROHC KYLSA KYROHA LEZCB NEN OSS SHR TBN TJK TTR TSK TKLI TKL TKCI TVN UZIBTL UZVL UZIBT UZV YKT ;

do
	mkdir crawl/$file
	python3 crawl.py https://ibtrussia.org/en/text?m=$file crawl/$file ; 
	python3 parse.py crawl/$file ../books2numbers.txt > files/$file.txt ;
	../../scripts/separate_punctuation.py files/$file.txt
done

