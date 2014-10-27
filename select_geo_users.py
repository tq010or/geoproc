#!/usr/bin/env python
"""
Given all geo tweet info (e.g., 
"""

import os
import sys
import geo_finder
#TODO: resolve python 2.6 issue
#from collections import Counter

try:
    import ujson as json
except ImportError:
    import json

gdict = dict();

#def get_most_common_item(lst):
#    data = Counter(lst)
#    return data.most_common(1)[0]

def get_most_common_item(lst):
    tmp_dict = dict()
    for i in lst:
        try:
            tmp_dict[i] += 1
        except KeyError:
            tmp_dict[i] = 1
    sorted_lst = sorted(tmp_dict.iteritems(), key = lambda k:k[1], reverse = True)
    return sorted_lst[0]

def merge_dict(udict):
    global gdict
    for uid in udict:
        if uid in gdict:
            gdict[uid].extends(udict[uid])
        else:
            gdict[uid] = udict[uid]

def rule1(ulist):
    # more than 7 geotagged tweets and at least 4 are from one location
    if len(ulist) < 7:
        return None
    loc_list = [geo_finder.lookup_city(coords[0], coords[1]) for coords in ulist]
    item, freq = get_most_common_item(loc_list)
    if not item or freq < 4:
        return None
    return item

def rule2():
    # most frequent geotagged tweet location agree with user-declared location
    return False

def rule3():
    # has to be english
    return False

def select_users():
    selected_users = dict()
    for uid in gdict:
        ulist = gdict[uid]
        #TODO; add multiple ordered rules for filtering
        #flag = rule1(ulist) | rule2(ulist) | rule3(ulist)
        loc = rule1(ulist)
        if loc:
            select_users[str(uid)] = loc
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

def _unit_test():
    lst = [2, 2, 2, 1, 2, 3, 4, 1, 2, 3, 5, 2, None, None, None, None, None]
    print get_most_common_item(lst)

if __name__ == "__main__":
    #_unit_test()
    main()
