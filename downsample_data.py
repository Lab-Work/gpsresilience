# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 13:36:41 2015

@author: Brian Donovan (briandonovan100@gmail.com)
"""
import cPickle as pickle

keys = [('Monday', 12), ('Monday', 4)]
with open('tmp_vectors.pickle', 'r') as f:
    d = pickle.load(f)


for key in keys:
    filename = "tmp_vectors_%s_%d.pickle" % key
    pace_timeseries, pace_grouped, weights_grouped, dates_grouped, trip_names, consistent_link_set = d
    
    pace_grouped_new = {}
    pace_grouped_new[key] = pace_grouped[key]
    
    weights_grouped_new = {}
    weights_grouped_new[key] = weights_grouped[key]

    dates_grouped_new = {}
    dates_grouped_new[key] = dates_grouped[key]

    new_d = [None, pace_grouped_new, weights_grouped_new, dates_grouped_new, None, None]

    with open(filename, 'w') as f:
        pickle.dump(new_d, f)