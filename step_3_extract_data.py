#!/usr/bin/env python
"""
Extract experiment data: tweet, time, lat, lon, city, uid, tid
Input: selected_user.json, GNIP dump .gz files
Output: line json records
"""

import os
import sys
from collections import Counter
from datetime import datetime

try:
    import ujson as json
except ImportError:
    import json
import geo_finder

udict = None
start_time = datetime(2011, 12, 31)


def get_wnd_id(ts, fmt):
    """    Map GNIP/Tweet tweet time to a particular window (determined by start time and window size)    """
    cur_time = datetime.strptime(ts, fmt)
    wnd_id = cur_time.strftime("%Y%m%d")
    return wnd_id

def proc_twitter(jobj):
    user = jobj["user"]
    uid = user["id_str"]
    if uid not in udict:
        return None
    loc = udict[uid]
    coords = geo_finder.lookup_coords(loc)
    lat = coords[0]
    lon = coords[1]
    tid = job["id_str"]
    tweet = jobj["text"]
    # date fmt: Sun Jun 20 22:56:08 +0000 2010
    time_stamp = get_wnd_id(jobj["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
    return (uid, tid, loc, lat, lon, time_stamp, tweet)
    
def proc_gnip(jobj):
    user = jobj["actor"]
    uid = user["id"].split(":")[-1]
    if uid not in udict:
        return None
    loc = udict[uid]
    coords = geo_finder.lookup_coords(loc)
    lat = coords[0]
    lon = coords[1]
    if "geo" in jobj:
        if "coordinates" in jobj["geo"]:
            coords = jobj["geo"]["coordinates"]
            lat = coords[0]
            lon = coords[1]
    tid = jobj["id"].split(":")[-1]
    tweet = jobj["body"]
    # date fmt: 2014-08-02T01:08:03.000Z
    time_stamp = get_wnd_id(jobj["postedTime"][:-5], "%Y-%m-%dT%H:%M:%S")
    return (uid, tid, loc, lat, lon, time_stamp, tweet)

def main():
    global udict 
    selected_user_file = sys.argv[1]
    udict = json.load(open(selected_user_file))

    for l in sys.stdin:
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
        print json.dumps(extracted_data)


if __name__ == "__main__":
    main()

