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

def proc_twitter(jobj):
    if "geo" not in jobj:
        return None
    geo = jobj["geo"]
    if not geo:
        return None
    coords = geo["coordinates"]
    lat = coords[0]
    lon = coords[1]
    user = jobj["user"]
    lang = user["lang"]
    location = user["location"]
    uid = user["id"]
    return (uid, lat, lon, lang, location)

def proc_gnip(jobj):
    if "geo" not in jobj:
        return None
    geo = jobj["geo"]
    if not geo:
        return None
    coords = geo["coordinates"]
    lat = coords[0]
    lon = coords[1]
    if lat == 0 and lon == 0:
        return None
    user = jobj["actor"]
    location = None
    if "location" in user:
        location = user["location"]["displayName"]
    lang = None
    if "languages" in user:
        lang = user["languages"][0]
    uid = user["id"].split(":")[-1]
    return (uid, lat, lon, lang, location)

def main():
    counter = 0
    acc_counter = 0
    output_file = sys.argv[1]
    print output_file
    for l in sys.stdin:
        counter += 1
        if counter == 1000000:
            acc_counter += counter;
            counter = 0
            print str(acc_counter) + " processed in " + output_file;
        try:        
            jobj = json.loads(l)
        except ValueError:
            continue

        extracted_data = None
        if "user" in jobj:
            extracted_data = proc_twitter(jobj)
        elif "actor" in jobj:
            extracted_data = proc_gnip(jobj)
        else:
            pass

        if not extracted_data:
            continue
        uid, lat, lon, lang, location = extracted_data
        if uid not in udict:
            udict[uid] = list()
        udict[uid].append((lat, lon, lang, location))
    json.dump(udict, open(output_file, "w"))

if __name__ == "__main__":
    main()
