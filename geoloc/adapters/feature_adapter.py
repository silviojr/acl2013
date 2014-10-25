#!/usr/bin/env
"""
Geolocation feature adapter
"""

import ujson as json
import os
pkg_path = os.environ["geoloc"]
liw_set = set(json.load(open("{0}/data/world.englang.optimised.fea.json".format(pkg_path))))

def extract_text_features(tweets):
    fea_dict = dict()
    for tweet in tweets:
        tokens = [token for token in tweet.lower().split(' ') if len(token) >= 3 and token.isalpha() and token in liw_set]
        for token in tokens:
            try:
                fea_dict[token] += 1
            except KeyError:
                fea_dict[token] = 1
    return fea_dict

#NOTE: optimised 4-gram characters for meta-data and unigram for text data
def extract_ngram_features(fea, ngram = 4):
    fea = "^" + fea.lower() + "$"
    nfeas = [] 
    for i in range(len(fea) - ngram + 1):
        nfeas.append(fea[i:i + ngram])
    # dummy features
    if not nfeas:
        nfeas = [fea]
    return nfeas 
