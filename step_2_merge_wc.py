#!/usr/bin/env python
"""
Merge word count for tweet data and get target word set
Input: dict JSON
Output: an overall wc JSON, a trunciated wc json
"""

import os
import sys
import json

def main():
    wc_folder = "../data/wc"
    MIN_NUM = 100

    wc_files = os.listdir(wc_folder)
    wc_dict = dict()
    for wc_file in wc_files:
        wc_file = os.path.join(wc_folder , wc_file)
        word_count_dict = json.load(open(wc_file))
        for w in word_count_dict:
            try:
                wc_dict[w] += word_count_dict[w]
            except KeyError:
                wc_dict[w] = word_count_dict[w]
    json.dump(wc_dict, open("../data/wc.all", "w"))
    w_set = wc_dict.keys()
    for w in w_set:
        if wc_dict[w] < MIN_NUM:
            del wc_dict[w]
    json.dump(wc_dict, open("../data/wc.{0}".format(MIN_NUM), "w"))


if __name__ == "__main__":
    main()

