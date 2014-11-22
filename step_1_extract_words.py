#!/usr/bin/env python
"""
Word counting for tweet data
Input: line JOSN
Output: word-count JSON
"""

import sys
import tokeniser
import json

t_tokeniser = tokeniser.MicroTokeniser()
output_file = sys.argv[1]

def filter_words(word):
    if word.isalpha():
	return True
    elif word.startswith("#"):
	return True
    elif word.startswith("@"):
	return True
    else:
	return False

def main():
    word_dict = dict()
    for l in sys.stdin:
        words = [word for word in t_tokeniser.tokenise(l[1:-1].strip().lower()) if filter_words(word)]
        for word in words:
            try:
                word_dict[word] += 1
            except KeyError:
                word_dict[word] = 1
    json.dump(word_dict, open(output_file, "w"))

if __name__ == "__main__":
    main()

