

for file in `ls bible.com`;

do
	python3 parse_new.py bible.com/$file ../books2numbers.txt > files/$file.txt
	../../scripts/separate_punctuation.py files/$file.txt
done