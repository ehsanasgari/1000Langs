#!/usr/bin/env python3

import sys
import io
import re
import collections


def word_frequency(handle):
    words = collections.Counter()
    for line in handle:
        if line.startswith('#'):
            continue
        line = line.rstrip('\n\r ')
        if not line or '\t' not in line:
            continue
        _, v = line.split('\t', 1)
        words.update(v.split())
    return words


def get_candidates(rest):
    result = [('', '', rest)]
    pre = []
    for index, r in enumerate(rest):
        if len(r) > 1:
            result.append((''.join(pre), '', rest[index:]))
            break
        if r in '.,;:?!':
            result.append((''.join(pre), r, rest[index+1:]))
            break
        else:
            result.append((''.join(pre), '', rest[index:]))
            if r.isupper():
                break
        pre.append(r)
    return result

SINGLES = re.compile(r'\s\S\s\S\s')

def main(args):
    handle = io.open(args[0], 'r+')
    frequency = word_frequency(handle)
    handle.seek(0)
    lines = handle.readlines()
    handle.seek(0)
    handle.truncate()
    for line in lines:
        if line.startswith('#'):
            handle.write(line)
            continue
        line = line.rstrip('\n\r ')
        if not line or '\t' not in line:
            handle.write(line)
            handle.write('\n')
            continue
        num, text = line.split('\t')
        match = SINGLES.search(text)
        if not match:
            handle.write(line)
            handle.write('\n')
            continue
        parts = text.split()
        new_parts = []
        while parts:
            base = parts[0]
            candidates = get_candidates(parts[1:])
            candidates.sort(key=lambda x: -frequency.get((base+x[0]), 0)*len(x[0]))
            choosen = candidates[0]
            #print(choosen)
            new_parts.append(base + choosen[0] + choosen[1])
            parts = choosen[2]
        print(line, file=sys.stderr)
        print('%s\t%s' % (num, ' '.join(new_parts)), file=sys.stderr)
        print('', file=sys.stderr)
        handle.write('%s\t%s\n' % (num, ' '.join(new_parts)))


if __name__ == '__main__':
    main(sys.argv[1:])
