import jpype
import pandas as pd
import numpy as np
import Levenshtein
import pyximport; pyximport.install()

from magellan.cython.test_functions import *
from magellan.utils.helperfunctions import remove_non_ascii

# list of sim functions supported : UPDATE LATER
sim_fn_names = ['jaccard', 'lev', 'cosine', 'monge_elkan', 'needleman_wunsch', 'smith_waterman',
                'smith_waterman_gotoh', 'jaro', 'jaro_winkler', 'soundex',
                'exact_match', 'rel_diff', 'abs_norm']

# abbreviations of sim functions
abb = ['jac', 'lev', 'cos', 'mel', 'nmw', 'sw',
       'swg', 'jar', 'jwn', 'sdx',
       'exm', 'rdf', 'anm']

# global function names
_global_sim_fns = pd.DataFrame({'function_name':sim_fn_names, 'short_name':abb})

# get similarity functions

def get_sim_funs_for_blocking():
    return get_sim_funs()
def get_sim_funs_for_matching():
    return get_sim_funs()

def get_sim_funs():
    fns = [jaccard,  lev, cosine, monge_elkan, needleman_wunsch, smith_waterman, smith_waterman_gotoh,
           jaro, jaro_winkler, soundex,
           exact_match, rel_diff, abs_norm]
    return dict(zip(sim_fn_names, fns))

# similarity measures

# set based
def _jaccard(arr1, arr2):
    if arr1 is None or arr2 is None:
        return np.NaN
    if not isinstance(arr1, list):
        arr1 = [arr1]
    if any(pd.isnull(arr1)):
        return np.NaN
    if not isinstance(arr2, list):
        arr2 = [arr2]
    if any(pd.isnull(arr2)):
        return np.NaN


    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.jaccard(arr1, arr2)

def jaccard(arr1, arr2):
    if arr1 is None or arr2 is None:
        return np.NaN
    if not isinstance(arr1, list):
        arr1 = [arr1]
    if any(pd.isnull(arr1)):
        return np.NaN
    if not isinstance(arr2, list):
        arr2 = [arr2]
    if any(pd.isnull(arr2)):
        return np.NaN
    return compute_jaccard_index(set(arr1), set(arr2))


def cosine(arr1, arr2):
    if arr1 is None or arr2 is None:
        return np.NaN
    if not isinstance(arr1, list):
        arr1 = [arr1]
    if any(pd.isnull(arr1)):
        return np.NaN
    if not isinstance(arr2, list):
        arr2 = [arr2]
    if any(pd.isnull(arr2)):
        return np.NaN

    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.cosine(arr1, arr2)




# string based
def _lev(s1, s2):
    if s1 is None or s2 is None:
        return np.NaN
    if pd.isnull(s1) or pd.isnull(s2):
        return np.NaN
    if isinstance(s1, basestring):
        s1 = remove_non_ascii(s1)
    if isinstance(s2, basestring):
        s2 = remove_non_ascii(s2)
    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.levenshtein(str(s1), str(s2))

def lev(s1, s2):
    if s1 is None or s2 is None:
        return np.NaN
    if pd.isnull(s1) or pd.isnull(s2):
        return np.NaN
    s1 = str(s1)
    s2 = str(s2)
    l1 = float(len(s1))
    l2 = float(len(s2))
    return 1.0 - Levenshtein.distance(s1, s2)/(max(l1, l2))




def jaro(s1, s2):
    if s1 is None or s2 is None:
        return np.NaN
    if pd.isnull(s1) or pd.isnull(s2):
        return np.NaN
    if isinstance(s1, basestring):
        s1 = remove_non_ascii(s1)
    if isinstance(s2, basestring):
        s2 = remove_non_ascii(s2)
    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.jaro(str(s1), str(s2))

def jaro_winkler(s1, s2):
    if s1 is None or s2 is None:
        return np.NaN
    if pd.isnull(s1) or pd.isnull(s2):
        return np.NaN
    if isinstance(s1, basestring):
        s1 = remove_non_ascii(s1)
    if isinstance(s2, basestring):
        s2 = remove_non_ascii(s2)
    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.jaroWinkler(str(s1), str(s2))

def monge_elkan(s1, s2):
    if s1 is None or s2 is None:
        return np.NaN
    if pd.isnull(s1) or pd.isnull(s2):
        return np.NaN
    if isinstance(s1, basestring):
        s1 = remove_non_ascii(s1)
    if isinstance(s2, basestring):
        s2 = remove_non_ascii(s2)
    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.mongeElkan(s1, s2)

def needleman_wunsch(s1, s2):
    if s1 is None or s2 is None:
        return np.NaN
    if pd.isnull(s1) or pd.isnull(s2):
        return np.NaN
    if isinstance(s1, basestring):
        s1 = remove_non_ascii(s1)
    if isinstance(s2, basestring):
        s2 = remove_non_ascii(s2)
    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.needlemanWunch(s1, s2)

def smith_waterman(s1, s2):
    if s1 is None or s2 is None:
        return np.NaN
    if pd.isnull(s1) or pd.isnull(s2):
        return np.NaN
    if isinstance(s1, basestring):
        s1 = remove_non_ascii(s1)
    if isinstance(s2, basestring):
        s2 = remove_non_ascii(s2)
    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.smithWaterman(s1, s2)

def smith_waterman_gotoh(s1, s2):
    if s1 is None or s2 is None:
        return np.NaN
    if pd.isnull(s1) or pd.isnull(s2):
        return np.NaN
    if isinstance(s1, basestring):
        s1 = remove_non_ascii(s1)
    if isinstance(s2, basestring):
        s2 = remove_non_ascii(s2)
    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.smithWatermanGotoh(s1, s2)

def soundex(s1, s2):
    if s1 is None or s2 is None:
        return np.NaN
    if pd.isnull(s1) or pd.isnull(s2):
        return np.NaN
    if isinstance(s1, basestring):
        s1 = remove_non_ascii(s1)
    if isinstance(s2, basestring):
        s2 = remove_non_ascii(s2)
    sim = jpype.JClass('build.SimilarityFunction')()
    return sim.soundex(s1, s2)










# boolean/string/numeric similarity measure
def exact_match(d1, d2):
    if d1 is None or d2 is None:
        return np.NaN
    if pd.isnull(d1) or pd.isnull(d2):
        return np.NaN
    if d1 == d2:
        return 1
    else:
        return 0

# numeric similarity measure
def rel_diff(d1, d2):
    if d1 is None or d2 is None:
        return np.NaN
    if pd.isnull(d1) or pd.isnull(d2):
        return np.NaN
    d1 = float(d1)
    d2 = float(d2)
    if d1 == 0.0 and d2 == 0.0:
        return 0
    else:
        x = abs(d1-d2)/(d1+d2)
        if x <= 10e-5:
            x = 0
        return 1.0 - x

# compute absolute norm similarity
def abs_norm(d1, d2):
    if d1 is None or d2 is None:
        return np.NaN
    if pd.isnull(d1) or pd.isnull(d2):
        return np.NaN
    d1 = float(d1)
    d2 = float(d2)
    if d1 == 0.0 and d2 == 0.0:
        return 0
    else:
        x =  1 - (abs(d1-d2)/max(d1, d2))

        if x <= 10e-5:
            x = 0
        #print 'returning 0'
        return x

#