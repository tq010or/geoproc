#!/usr/bin/env python
"""
Calculate temporal variance
"""

import ujson as json
import langid
import tokeniser
import random
import geo_finder

t_tokeniser = tokeniser.MicroTokeniser()

wdict = dict()
k = 10

def calc_localness(loc_list):
    loc_score = 0.0
    if len(loc_list) < k:
        return "S"
    samples = random.sample(loc_list, k)
    pair_list = [(l1, l2) for l1 in samples for l2 in samples if l1 != l2]
    res_list = []
    for pair in pair_list:
        l1 = pair[0]
        l2 = pair[1]
        lat1 = l1[0]
        lon1 = l1[1]
        lat2 = l2[0]
        lon2 = l2[1]
        res_list.append(geo_finder.calc_dist_degree(lat1, lon1, lat2, lon2))
    # get median
    res_list.sort()
    return res_list[len(res_list) / 2]

def main():
    # construct matrix
    ts_set = set()
    for l in open("../data/2012.flat.rec.json"):
        jobj = json.loads(l)
        ts = jobj[0]
        ts_set.add(ts)
        lat = jobj[3]
        lon = jobj[4]
        text = jobj[5]
        if langid.classify(text)[0] != "en":
            continue
        tokens = [token.isalpha() for token in t_tokeniser.tokenise(text.lower())]
        for token in tokens:
            if token not in wdict:
                wdict[token] = dict()
            try:
                wdict[token][ts].append((lat, lon))
            except KeyError:
                wdict[token][ts] = [(lat, lon)]
    # generate data
    ts_list = list(ts_set)
    ts_list.sort()
    print ts_list
    with open("../data/2012.var", "w") as fw:
        # header
        fw.write("{0}\t{1}\n".format(word, "\t".join(map(str, ts_list))))
        # rows
        for w in wdict:
            rec = [w]
            loc_score_list = []
            for ts in ts_list:
                loc_score = "N"
                if ts in wdict[w]:
                    loc_score = calc_localness(wdict[w][ts])
                loc_score_list.append(loc_score)
            fw.write("{0}\t{1}\n".format(word, "\t".join(map(str, loc_score_list))))

if __name__ == "__main__":
    main()
