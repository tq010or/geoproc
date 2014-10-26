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
    for l in sys.stdin:
        jobj = json.loads(l)
        if jobj["geo"]:
            print l
            break

if __name__ == "__main__":
    main()
