import logging

import pandas as pd

from collections import OrderedDict
from magellan.blocker.blocker import Blocker
from magellan import MTable
import magellan as mg
import math
import pyprind

class RuleBasedBlocker(Blocker):

    def __init__(self, *args, **kwargs):
        feature_table = kwargs.pop('feature_table', None)
        self.feature_table = feature_table
        self.rules = OrderedDict()

        # meta data : should be removed if they are not useful.
        self.rule_source = OrderedDict()
        self.rule_cnt = 0

        super(Blocker, self).__init__(*args, **kwargs)

    def create_rule(self, conjunct_list, feature_table=None):
        if feature_table is None and self.feature_table is None:
            logging.getLogger(__name__).error('Either feature table is given as a parameter or use set_feature_table to '
                                          'set feature table')
            return False
        # set the name
        name = '_rule_'+ str(self.rule_cnt)
        self.rule_cnt += 1
        # create function str
        fn_str = "def " + name + "(ltuple, rtuple):\n"
        # add 4 tabs
        fn_str += '    '
        fn_str += 'return ' + ' and '.join(conjunct_list)

        if feature_table is not None:
            feat_dict = dict(zip(feature_table['feature_name'], feature_table['function']))
        else:
            feat_dict = dict(zip(self.feature_table['feature_name'], self.feature_table['function']))

        exec fn_str in feat_dict

        return feat_dict[name], name, fn_str

    def add_rule(self, conjunct_list, feature_table):
        """
        Add rule to rule-based blocker

        Parameters
        ----------
        conjunct_list : list of string, and each conjunct is a predicate
        feature_table : pandas dataframe containing feature information

        Returns
        -------
        status : boolean, returns True if the rule addition was successful

        Example
        -------
        feature_table = mg.get_features_for_blocking(A, B)
        rb = mg.RuleBasedBlocker()
        rb.add_rule(['name_name_mel(ltuple, rtuple) < 0.6', 'zipcode_zipcode_exm(ltuple, rtuple) != 1'], feature_table)
        """
        if not isinstance(conjunct_list, list):
            conjunct_list = [conjunct_list]

        fn, name, fn_str = self.create_rule(conjunct_list, feature_table)

        self.rules[name] = fn
        self.rule_source[name] = fn_str

        return True

    def delete_rule(self, rule_name):
        if rule_name not in self.rules.keys():
            logging.getLogger(__name__).error('Rule name not present in current set of rules')
            return False

        del self.rules[rule_name]
        del self.rule_source[rule_name]
        return True

    def view_rule(self, rule_name):
        if rule_name not in self.rules.keys():
            logging.getLogger(__name__).error('Rule name not present in current set of rules')
        print(self.rule_source[rule_name])

    def get_rule_names(self):
        return self.rules.keys()

    def get_rule(self, rule_name):
        if rule_name not in self.rules.keys():
            logging.getLogger(__name__).error('Rule name not present in current set of rules')
        return self.rules[rule_name]

    def set_feature_table(self, feature_table):
        if self.feature_table is not None:
            logging.getLogger(__name__).warning('Feature table is already set, changing it now will not recompile '
                                                'existing rules')
        self.feature_table = feature_table
        return True


    def block_tables(self, ltable, rtable, l_output_attrs=None, r_output_attrs=None):
        """
        Block two tables

        Parameters
        ----------
        ltable, rtable : MTable
            Input MTables
        l_output_attrs, r_output_attrs : list (of strings), defaults to None
            attribute names to be included in the output table

        Returns
        -------
        blocked_table : MTable

        Notes
        -----
        Output MTable contains the following three attributes
            * _id
            * id column from ltable
            * id column from rtable

        Also, the properties of blocked table is updated with following key-value pairs
            * ltable - ref to ltable
            * rtable - ref to rtable
            * key
            * foreign_key_ltable - string, ltable's  id attribute name
            * foreign_key_rtable - string, rtable's id attribute name
        """

        # do integrity checks
        l_output_attrs, r_output_attrs = self.check_attrs(ltable, rtable, l_output_attrs, r_output_attrs)
        block_list = []
        if mg._verbose:
            count = 0
            per_count = math.ceil(mg._percent/100.0*len(ltable)*len(rtable))
        elif mg._progbar:
            bar = pyprind.ProgBar(len(ltable)*len(rtable))

        l_df = ltable.set_index(ltable.get_key(), drop=False)
        r_df = rtable.set_index(rtable.get_key(), drop=False)
        l_dict = {}
        for k, r in l_df.iterrows():
            l_dict[k] = r
        r_dict = {}
        for k, r in r_df.iterrows():
            r_dict[k] = r

        lid_idx = ltable.get_attr_names().index(ltable.get_key())
        rid_idx = rtable.get_attr_names().index(rtable.get_key())
        for l_t in ltable.itertuples(index=False):
            for r_t in rtable.itertuples(index=False):
                if mg._verbose:
                    count += 1
                    if count%per_count == 0:
                        print str(mg._percent*count/per_count) + ' percentage done !!!'
                elif mg._progbar:
                    bar.update()


                l = l_dict[l_t[lid_idx]]
                r = r_dict[r_t[rid_idx]]
                # check whether it passes

                res = self.apply_rules(l, r)
                if res is True:
                    d = OrderedDict()
                    # add left id first
                    ltable_id = 'ltable.' + ltable.get_key()
                    d[ltable_id] = l[ltable.get_key()]

                    # add right id
                    rtable_id = 'rtable.' + rtable.get_key()
                    d[rtable_id] = r[rtable.get_key()]

                    # add left attributes
                    if l_output_attrs:
                        l_out = l[l_output_attrs]
                        l_out.index = 'ltable.'+l_out.index
                        d.update(l_out)

                    # add right attributes
                    if r_output_attrs:
                        r_out = r[r_output_attrs]
                        r_out.index = 'rtable.'+r_out.index
                        d.update(r_out)
                    block_list.append(d)


        candset = pd.DataFrame(block_list)
        ret_cols = self.get_attrs_to_retain(ltable.get_key(), rtable.get_key(), l_output_attrs, r_output_attrs)

        if len(candset) > 0:
            candset = MTable(candset[ret_cols])
        else:
            candset = MTable(candset, columns=ret_cols)

        # add key
        #key_name = candset._get_name_for_key(candset.columns)
        #candset.add_key(key_name)

        # set metadata
        candset.set_property('ltable', ltable)
        candset.set_property('rtable', rtable)
        candset.set_property('foreign_key_ltable', 'ltable.'+ltable.get_key())
        candset.set_property('foreign_key_rtable', 'rtable.'+rtable.get_key())
        return candset


    def block_candset(self, vtable):
        """
        Block candidate set (virtual MTable)

        Parameters
        ----------
        vtable : MTable
            Input candidate set

        Returns
        -------
        blocked_table : MTable


        Notes
        -----
        Output MTable contains the following three attributes
            * _id
            * id column from ltable
            * id column from rtable

        Also, the properties of blocked table is updated with following key-value pairs
            * ltable - ref to ltable
            * rtable - ref to rtable
            * key
            * foreign_key_ltable - string, ltable's  id attribute name
            * foreign_key_rtable - string, rtable's id attribute name
        """

        ltable = vtable.get_property('ltable')
        rtable = vtable.get_property('rtable')

        self.check_attrs(ltable, rtable, None, None)
        l_key = vtable.get_property('foreign_key_ltable')
        r_key = vtable.get_property('foreign_key_rtable')

        # set the index and store it in l_tbl/r_tbl
        l_tbl = ltable.set_index(ltable.get_key(), drop=False)
        r_tbl = rtable.set_index(rtable.get_key(), drop=False)

        # create look up table for quick access of rows
        l_dict = {}
        for k, r in l_tbl.iterrows():
            l_dict[k] = r
        r_dict = {}
        for k, r in r_tbl.iterrows():
            r_dict[k] = r
        # keep track of valid ids
        valid = []
        # iterate candidate set and process each row
        if mg._verbose:
            count = 0
            per_count = math.ceil(mg._percent/100.0*len(vtable))
        elif mg._progbar:
            bar = pyprind.ProgBar(len(vtable))

        column_names = list(vtable.columns)
        lid_idx = column_names.index(l_key)
        rid_idx = column_names.index(r_key)

        for row in vtable.itertuples(index=False):
            if mg._verbose:
                count += 1
                if count%per_count == 0:
                    print str(mg._percent*count/per_count) + ' percentage done !!!'
            elif mg._progbar:
                bar.update()

            l_row = l_dict[row[lid_idx]]
            r_row = r_dict[row[rid_idx]]

            res = self.apply_rules(l_row, r_row)
            if res is True:
                valid.append(True)
            else:
                valid.append(False)
        # should be modified
        if len(vtable) > 0:
            out_table = MTable(vtable[valid], key=vtable.get_key())
        else:
            out_table = MTable(columns=vtable.columns, key=vtable.get_key())
        out_table.set_property('ltable', ltable)
        out_table.set_property('rtable', rtable)
        out_table.set_property('foreign_key_ltable', vtable.get_property('foreign_key_ltable'))
        out_table.set_property('foreign_key_rtable', vtable.get_property('foreign_key_rtable'))
        return out_table

    def block_tuples(self, ltuple, rtuple):
        return not self.apply_rules(ltuple, rtuple)


    # helper functions
    def check_attrs(self, ltable, rtable, l_output_attrs, r_output_attrs):
        # check keys are set
        assert ltable.get_key() is not None, 'Key is not set for left table'
        assert rtable.get_key() is not None, 'Key is not set for right table'
        # check output columns form a part of left, right tables
        if l_output_attrs:
            if not isinstance(l_output_attrs, list):
                l_output_attrs = [l_output_attrs]
            assert set(l_output_attrs).issubset(ltable.columns) is True, 'Left output attributes ' \
                                                                         'are not in left table'
            l_output_attrs = [x for x in l_output_attrs if x not in [ltable.get_key()]]

        if r_output_attrs:
            if not isinstance(r_output_attrs, list):
                r_output_attrs = [r_output_attrs]
            assert set(r_output_attrs).issubset(rtable.columns) is True, 'Right output attributes ' \
                                                                         'are not in right table'
            r_output_attrs = [x for x in r_output_attrs if x not in [rtable.get_key()]]

        return l_output_attrs, r_output_attrs




    def apply_rules(self, ltuple, rtuple):
        for fn in self.rules.values():
            # here if the function returns true, then the tuple pair must be dropped.
            # At the implementation level, what we want are the tuple pairs that passes
            res =  fn(ltuple, rtuple)
            if res is True:
                return False
        return True


    def get_attrs_to_retain(self, l_id, r_id, l_col, r_col):
        ret_cols=[]
        ret_cols.append('ltable.' + l_id)
        ret_cols.append('rtable.' + r_id)
        if l_col:
            ret_cols.extend(['ltable.'+c for c in l_col])
        if r_col:
            ret_cols.extend(['rtable.'+c for c in r_col])
        return ret_cols



