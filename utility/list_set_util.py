__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__email__ = "asgari@berkeley.edu"
__project__ = "LLP - DiTaxa"
__website__ = "https://llp.berkeley.edu/ditaxa/"

import operator
import numpy as np

def get_intersection_of_list(list_of_list_features):
    return list(set.intersection(*map(set, list_of_list_features)))

def get_max_of_dict(inp):
    return max(inp.items(), key=operator.itemgetter(1))[0]

def argsort(seq, rev=False):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__, reverse=rev)

def sampling_from_dict(score_dict, N):
    summation=np.sum(list(score_dict.values()))
    keys=list(score_dict.keys())
    keys.sort()
    probDict={k:(s/summation) for k,s in score_dict.items()}
    prob_list=[probDict[k] for k in keys]
    return np.random.choice(keys, N, prob_list).tolist()

def get_n_grams(sentence,n):
    all_ngrams = [(sentence[i:i + n]) for i in range(len(sentence) - n + 1)]
    return [all_ngrams[i::n] for i in range(n)]

def remove_keys_from_dict(entries, the_dict):
    for key in entries:
        if key in the_dict:
            del the_dict[key]
