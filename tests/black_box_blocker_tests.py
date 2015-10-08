from nose.tools import *
from tests import mg, path_for_A, path_for_B
from magellan.feature.simfunctions import  monge_elkan, jaccard
from magellan.feature.tokenizers import tok_qgram
def block_fn(x, y):
    if (monge_elkan(x['name'], y['name']) < 0.4):
        return True
    else:
        return False

def test_bb_block_tables():
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    bb = mg.BlackBoxBlocker()
    bb.set_black_box_function(block_fn)
    C = bb.block_tables(A, B, 'zipcode', 'zipcode')
    s1 = sorted(['_id', 'ltable.ID', 'rtable.ID', 'ltable.zipcode', 'rtable.zipcode'])
    assert_equal(s1, sorted(C.columns))
    assert_equal(C.get_key(), '_id')
    assert_equal(C.get_property('foreign_key_ltable'), 'ltable.ID')
    assert_equal(C.get_property('foreign_key_rtable'), 'rtable.ID')

    feature_table = mg.get_features_for_blocking(A, B)
    A['dummy'] = 1
    B['dummy'] = 1
    ab = mg.AttrEquivalenceBlocker()
    D = ab.block_tables(A, B, 'dummy','dummy')
    fv = mg.extract_feat_vecs(D,  feat_table=feature_table)
    expected_ids = fv.ix[(fv.name_name_mel >= 0.4) ,
      ['ltable.ID', 'rtable.ID']]
    actual_ids = C[['ltable.ID', 'rtable.ID']]
    ids_exp = list(expected_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    ids_act = list(actual_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    assert_equal(cmp(ids_exp, ids_act), 0)

def test_bb_block_candset():
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    ab = mg.AttrEquivalenceBlocker()
    E = ab.block_tables(A, B, 'zipcode', 'zipcode')
    bb = mg.BlackBoxBlocker()
    bb.set_black_box_function(block_fn)
    C = bb.block_candset(E)
    feature_table = mg.get_features_for_blocking(A, B)
    fv = mg.extract_feat_vecs(C, feat_table=feature_table)
    expected_ids = fv.ix[(fv.name_name_mel >= 0.4) ,
      ['ltable.ID', 'rtable.ID']]
    actual_ids = C[['ltable.ID', 'rtable.ID']]
    ids_exp = list(expected_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    ids_act = list(actual_ids.set_index(['ltable.ID', 'rtable.ID']).index.values)
    assert_equal(cmp(ids_exp, ids_act), 0)

def test_bb_block_tuples():
    A = mg.read_csv(path_for_A, key='ID')
    B = mg.read_csv(path_for_B, key='ID')
    bb = mg.BlackBoxBlocker()
    bb.set_black_box_function(block_fn)
    assert_equal(bb.block_tuples(A.ix[0], B.ix[0]), True)
    assert_equal(bb.block_tuples(A.ix[2], B.ix[1]), False)



