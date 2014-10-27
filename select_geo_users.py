#!/usr/bin/env python
"""
Given all geo tweet info (e.g., 
"""

import os
import sys
import geo_finder
from collections import Counter

try:
    import ujson as json
except ImportError:
    import json

gdict = dict();

def get_most_common_item(lst):
    data = Counter(lst)
    return data.most_common(1)[0]

def merge_dict(udict):
    global gdict
    for uid in udict:
        if uid in gdict:
            gdict[uid].extends(udict[uid])
        else:
            gdict[uid] = udict[uid]

def rule1(ulist):
    # more than 5 geotagged tweets and at least 3 are from one location
    if len(ulist) < 5:
        return False
    loc_list = [geo_finder.lookup_city(coords[0], coords[1]) for coords in ulist]
    item, freq = get_most_common_item(loc_list)
    if not item or freq < 3:
        return False
    return True

def rule2():
    # most frequent geotagged tweet location agree with user-declared location
    pass

def rule3():
    # has to be english
    return False

def select_users():
    selected_users = []
    for uid in gdict:
        ulist = gdict[uid]
        flag = rule1(ulist) | rule2(ulist) | rule3(ulist)
        if flag:
            select_users.append(uid)
    return selected_users


def main():
    output_file = sys.argv[1]
    for geo_file in sys.stdin:
        print "merging", geo_file
        merge_dict(json.load(open(geo_file)))
    print "merging done"
    selected_users = select_users()
    print len(selected_users), "users are selected"
    json.dump(selected_users, open(output_file, "w"))

if __name__ == "__main__":
    main()
