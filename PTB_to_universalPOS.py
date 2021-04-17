# -*- coding: utf-8 -*-
#!usr/bin/env python3

import re
import sys

"""
sys.argv[1] = annotated Stanford Penn Treebank source file
sys.argv[2] = correlation table file between Penn Treebank POS and universal POS
You may find in this repository a correlation table named named POSTags_PTB_Universal_Linux.txt
Conversion with regexp only
In fact, you can use NLTK module with map_tag function for the same purpose
"""

def load_pos_table():

    try:
         
        with open(sys.argv[2], 'r', encoding='utf-8') as universal:

            dict_pos = {}
            for sent in universal.readlines():
                for line in sent.splitlines():
                    cut = line.strip().split()
                    dict_pos[cut[1]] = dict_pos.get(cut[1], list()) + [cut[0]]

        return dict_pos

    except Exception as erreur:
        print(f'load_pos_table : {erreur}')

def convert_tag(source_file, target_file, pos_table):

    try:
        with open(source_file, 'r', encoding='utf-8') as sample_stan, open(target_file, 'w', encoding='utf-8') as result_file:

            for line in sample_stan.readlines():

                rx_dctvals = {}
                for key, val in pos_table.items():
                    rx_dctvals[re.compile("|".join(sorted([to_regex(v) for v in val], key=len, reverse=True)))] = key

                for rx, repl in rx_dctvals.items():
                    line = rx.sub(repl.replace('\\', '\\\\'), line)

                result_file.write(line)

    except Exception as erreur:
        print(f'convert_tag: {erreur}')

def to_regex(x):

    r = []
    if x[0].isalnum() or x[0] == '_':
        r.append(r'(?<![^\W_])')
    else:
        if any(l.isalnum() or l=='_' for l in x):
            r.append(r'\B')
    r.append(re.escape(x))
    if x[-1].isalnum() or x[-1] == '_':
        r.append(r'\b')
    else:
        if any(l.isalnum() or l=='_' for l in x):
            r.append(r'\B')
    return "".join(r)

# fonction principale
def main():

    pos_table = load_pos_table()

    convert_tag(sys.argv[1], sys.argv[1] + 'result', pos_table)


if __name__ == '__main__':
    main()
