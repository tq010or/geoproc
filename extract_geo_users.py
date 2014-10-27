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
    output_file = sys.argv[1]
    for l in sys.stdin:
        jobj = json.loads(l)
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
