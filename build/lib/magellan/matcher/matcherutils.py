from collections import OrderedDict
import sklearn.cross_validation as cv
import numpy as np

from magellan import MTable
import time
import math
def train_test_split(labeled_data, train_proportion = 0.5, random_state=None):
    """
    Split MTable into Train and Test

    Parameters
    ----------
    labeled_data : MTable
    train_proportion : float, in the range 0-1. Proportion of train tuples, by default set to 0.5
    random_state : int, Pseudo-random number generator state for random sampling

    Returns
    -------
    result: Python dictionary with two keys: train, test. The value for each key is
    a MTable containing tuples for train and test respectively.
    """

    num_rows = len(labeled_data)
    assert train_proportion >=0 and train_proportion <= 1, " Train proportion is expected to be between 0 and 1"
    train_size = int(math.floor(num_rows*train_proportion))
    test_size = int(num_rows - train_size)

    idx_values = np.array(labeled_data.index.values)
    idx_train, idx_test = cv.train_test_split(idx_values, test_size=test_size, train_size=train_size,
                                              random_state=random_state)
    # create a MTable for train and test data
    lbl_train = MTable(labeled_data.ix[idx_train], key=labeled_data.get_key())
    lbl_test = MTable(labeled_data.ix[idx_test], key=labeled_data.get_key())

    # propogate properties
    lbl_train.set_property('key', labeled_data.get_key())
    lbl_train.set_property('ltable', labeled_data.get_property('ltable'))
    lbl_train.set_property('rtable', labeled_data.get_property('rtable'))
    lbl_train.set_property('foreign_key_ltable', labeled_data.get_property('foreign_key_ltable'))
    lbl_train.set_property('foreign_key_rtable', labeled_data.get_property('foreign_key_rtable'))

    lbl_test.set_property('key', labeled_data.get_key())
    lbl_test.set_property('ltable', labeled_data.get_property('ltable'))
    lbl_test.set_property('rtable', labeled_data.get_property('rtable'))
    lbl_test.set_property('foreign_key_ltable', labeled_data.get_property('foreign_key_ltable'))
    lbl_test.set_property('foreign_key_rtable', labeled_data.get_property('foreign_key_rtable'))

    result = OrderedDict()
    result['train'] = lbl_train
    result['test'] = lbl_test

    return result

def get_ts():
    t = int(round(time.time()*1e10))
    return str(t)[::-1]



