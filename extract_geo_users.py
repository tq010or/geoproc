#!/usr/bin/env python
"""
Extract geotagged users from GNIP 10% Twitter feeds
Input: a GNIP .gz file
Output: a serialised {uid: {coord1, coord2, ...}, loc}
"""

import os
import sys
try:
    import ujson as json
except ImportError:
    import json


udict = dict();

def main():
    counter = 0
    acc_counter = 0
    output_file = sys.argv[1]
    print output_file
    for l in sys.stdin:
        counter += 1
        if counter == 10000:
            acc_counter += counter;
            counter = 0
            print str(acc_counter) + " processed in " + output_file;
        try:        
            jobj = json.loads(l)
        except ValueError:
            print l
            continue
        if "geo" not in jobj:
            continue
        geo = jobj["geo"]
        if not geo:
            continue
        coords = geo["coordinates"]
        lat = coords[0]
        lon = coords[1]
        user = jobj["user"]
        lang = user["lang"]
        location = user["location"]
        uid = user["id"]
        if uid not in udict:
            udict[uid] = list()
        udict[uid].append((lat, lon, lang, location))
    json.dump(udict, open(output_file, "w"))

if __name__ == "__main__":
    main()
