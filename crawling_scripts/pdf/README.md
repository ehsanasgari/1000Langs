To parse bibles which are only available as PDF files you need first to
get a textual representation of the PDF. To this end I used the program
`pdftotext` which under Linux is contained in the poppler-tools package.
Under Mac OSX this program is part of the MacPorts or homebrew package
poppler.

This program can produces several different output formats:

- plain text
- HTML
- XML

As of now the XML output served me best and the example script included
in this directory requires XML as input.

Additionally there is a script `join_single_letters.py`, which tries to
address the problem, that sometimes words in the XML appear spaced out
into single letters. The result isn't perfect, though.
