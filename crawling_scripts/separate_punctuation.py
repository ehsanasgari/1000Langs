#!/usr/bin/env python2

import sys
import io
import re, sre_constants
import collections
import unicodedata
from itertools import chain

def get_to_seperate(filename):
    words = collections.Counter()
    with io.open(filename, encoding='utf8') as f:
        for line in f:
            if line.startswith('#'):
                continue
            line = line.rstrip('\n\r ')
            if not line or '\t' not in line:
                continue
            _, v = line.split('\t', 1)
            words.update(v.split())
    to_seperate = collections.Counter()
    to_keep = collections.Counter()
    for word in words:
        left = 0
        while left < len(word):
            if word[left].isalnum() or unicodedata.category(word[left])[0] == 'M':
                break
            left += 1
        right = len(word)
        while right > left:
            if word[right-1].isalnum() or unicodedata.combining(word[right-1]) > 0 \
               or unicodedata.category(word[right-1])[0] == 'M':
                break
            right -= 1
        if left == 0 and right == len(word) or left == right:
            continue
        remaining = word[left:right]
        if remaining in words and words[word] < words[remaining]:
            for c in chain(word[:left], word[right:]):
                to_seperate[c] += words[word]
#            to_seperate.update(chain(word[:left], word[right:]))
        else:
            for c in chain(word[:left], word[right:]):
                to_keep[c] += words[word]
#            to_keep.update(chain(word[:left], word[right:]))
    return to_seperate, to_keep


def has_alpha(verse, run, direction, limit):
    while run != limit:
        if verse[run].isalpha():
            return True
        if verse[run].isspace():
            return False
        run += direction
    return False


def seperate(filename, to_seperate):
    if ']' in to_seperate:
        to_seperate.remove(']')
        to_seperate.insert(0, ']') # ']' as first character in character set [...] is taken literal
    if '\\' in to_seperate:
        to_seperate.remove('\\')
        to_seperate.append('\\\\') # properly escaped
    if '-' in to_seperate:
        to_seperate.remove('-')
        to_seperate.append('-') # '-' as last character in character set [...] is taken literal
        
    try:
        pattern = re.compile(u'[' + ''.join(to_seperate) + ']+')
    except:
        print ('sep>', to_seperate)
        print ('sep>', ''.join(to_seperate).encode('utf8'))
        return
    with io.open(filename, 'r+', encoding='utf8') as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        for line in lines:
            if line.startswith('#'):
                f.write(line)
                continue
            line = line.rstrip(' \n\r')
            if not line:
                continue
            if '\t' not in line:
                f.write(line + '\n')
                continue
            verse_number, verse = line.split('\t', 1)
            matches = list(pattern.finditer(verse))
            matches.reverse()
            for match in matches:
                left_boundary = match.start() == 0 or verse[match.start()-1].isspace()
                right_boundary = match.end() == len(verse) or verse[match.end()].isspace()
                if not (left_boundary or right_boundary):
                    continue
                if right_boundary and not (has_alpha(verse, match.start()-1, -1, -1) or \
                    verse[match.start()-1].isdigit()):
                    continue
                if left_boundary and not (has_alpha(verse, match.end(), 1, len(verse)) or \
                    verse[match.end()].isdigit()):
                    continue
                replacement = ''
                if match.start() == 0 or verse[match.start()-1].isspace():
                    replacement = ''.join(c + ' ' for c in match.group())
                elif match.end() == len(verse) or verse[match.end()].isspace():
                    replacement = ''.join(' ' + c for c in match.group())
                verse = verse[:match.start()] + replacement + verse[match.end():]
            f.write('%s\t%s\n' % (verse_number, ' '.join(verse.split(' '))))


def main(args):
    if '-l' in args:
        args.remove('-l')
        only_list = True
    else:
        only_list = False

    keep = []
    if '-k' in args:
        index = args.index('-k') + 1
        keep = unicode(args[index], 'utf8')
        args[index-1:index+1] = []

    always_seperate = []
    if '-s' in args:
        index = args.index('-s') + 1
        always_seperate = unicode(args[index], 'utf8')
        args[index-1:index+1] = []

    print ('--', args[0])

    to_seperate, to_keep = get_to_seperate(args[0])
    key_list = sorted(to_seperate)

    for s in key_list[:]:
        if s not in always_seperate and (to_seperate[s] *2 < to_keep[s] or s in keep):
            key_list.remove(s)
        name = unicodedata.name(s, 'Unknown codepoint')
        print ('%s %6i %6i %5s U+%04x %s' % (s.encode('utf8'), to_seperate[s], to_keep[s],
                                            s in key_list, ord(s), name))
    if only_list:
        sys.exit(0)

    if key_list:
        seperate(args[0], key_list)
    else:
        print ('Nothing to seperate')


if __name__ == '__main__':
    main(sys.argv[1:])
