#!/usr/bin/env python
"""
Extract experiment data: tweet, time, location (lat, lon, city), uid, tid
Input: selected_user.json, GNIP dump .gz files
Output: line json records
"""

import os
import sys
from collections import Counter

try:
    import ujson as json
except ImportError:
    import json

udict = None

def proc_twitter(jobj):
    user = jobj["user"]
    uid = user["id_str"]
    if uid not in udict:
        return None
    loc = udict[uid]
    tid = job["id_str"]
    tweet = jobj["text"]
    #TODO: adapt time to yyyy-mm-dd-hh-mm-ss
    time_stamp = jobj["created_at"]
    return (uid, tid, loc, time_stamp, tweet)
    
def proc_gnip(jobj):
    user = jobj["actor"]
    uid = user["id"].split(":")[-1]
    if uid not in udict:
        return None
    loc = udict[uid]
    tid = jobj["id"].split(":")[-1]
    tweet = jobj["body"]
    #TODO: adapt time to yyyy-mm-dd-hh-mm-ss
    time_stamp = jobj["postedTime"]
    return (uid, tid, loc, time_stamp, tweet)

def main():
    global udict 
    selected_user_file = sys.argv[1]
    output_file = sys.argv[2]
    udict = json.load(open(selected_user_file))

    with open(output_file, "w") as fw:
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
            fw.write("{0}\n".format(json.dumps(extracted_data)))


if __name__ == "__main__":
    main()

