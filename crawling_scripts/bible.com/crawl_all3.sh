#!/bin/bash

for file in 564/MRK.1 1044/MRK.1 1110/MRK.1 1215/MRK.1 1229/MRK.1 1374/MRK.1 1376/MRK.1 885/LUK.1 1412/LUK.1 1478/LUK.1 1559/LUK.1 1565/LUK.1 1592/LUK.1 1651/LUK.1 1652/LUK.1 1256/GEN.1 1380/GEN.1 1426/GEN.1 1465/GEN.1 1430/GEN.1 1473/GEN.1 1543/GEN.1 1545/GEN.1 1555/GEN.1 1557/GEN.1 1644/GEN.1 1700/GEN.1 1712/GEN.1 1421/EXO.2 1640/ACT.1 1254/RUT.1 1485/RUT.1 1649/RUT.1 1498/JHN.1 1500/JHN.1 1507/JHN.1 1653/JHN.1 1658/JHN.1 852/MAT.1 1311/MAT.1 1317/MAT.1 1319/MAT.1 1328/MAT.1 1337/MAT.1 1350/MAT.1 1377/MAT.1 1384/MAT.1 1552/MAT.1 1680/MAT.1 ;

#for file in 46/GEN.1 48/GEN.1 40/GEN.1 41/GEN.1 414/GEN.1 47/GEN.1 139/GEN.1 140/GEN.1 1392/GEN.1 36/GEN.1 ;

do
	nr=`expr "$file" : '\([0-9]*\)'`
	mkdir -p /mounts/data/proj/asgari/dissertation/git_repos/biblefiles/$nr
	python3 crawl.py https://www.bible.com/de/bible/$file /mounts/data/proj/asgari/dissertation/git_repos/biblefiles/$nr
	python3 parse_new.py /mounts/data/proj/asgari/dissertation/git_repos/biblefiles/$nr /mounts/data/proj/asgari/dissertation/git_repos/1000langs/crawling_scripts/books2numbers.txt > /mounts/data/proj/asgari/dissertation/git_repos/biblefiles/$nr.txt
	python3 ../separate_punctuation.py /mounts/data/proj/asgari/dissertation/git_repos/biblefiles/$nr.txt
done

