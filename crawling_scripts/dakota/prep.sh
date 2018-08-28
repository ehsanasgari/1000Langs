#!/usr/bin/bash

perl -pi -e 's/_+//g' test.txt
perl -pi -e 's/Dakota Bible Home//g' test.txt

perl -pi -e 's/^\n//sg' test.txt
perl -pi -e 's/^(\d)\t/0\1\t/sg' test.txt
perl -pi -e 's/^(\d)/0\1/g' test.txt
perl -pi -e 's/WICOWOYAKE (\d+)\.$/WICOWOYAKE\t\1/g' test.txt
perl -pi -e 's/WICOWOYAKE\t(\d)$/WICOWOYAKE\t0\1/g' test.txt
perl -pi -e 's/WICOWOYAKE\t/WICOWOYAKE\t0/g' test.txt
