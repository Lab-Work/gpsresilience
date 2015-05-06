# -*- coding: utf-8 -*-
"""
Created on Tue May  5 12:31:30 2015

@author: Brian Donovan (briandonovan100@gmail.com)
"""

from hmmlearn.hmm import MultinomialHMM
from numpy import array

from tools import *




def get_all_events(states, global_pace_timeseries, expected_pace_timeseries):
    currently_in_event = False
    for i in xrange(len(states)):
        
        if(not currently_in_event and states[i]==1):
            event_start_id = i
            currently_in_event = True
        





def detect_events_hmm(mahal_timeseries, c_timeseries, global_pace_timeseries):
    #Sort the keys of the timeseries chronologically    
    sorted_dates = sorted(mahal_timeseries)
    
    
    (expected_pace_timeseries, sd_pace_timeseries) = getExpectedPace(global_pace_timeseries)    

    #Generate the list of values of R(t)
    mahal_list = [mahal_timeseries[d] for d in sorted_dates]
    c_list = [c_timeseries[d] for d in sorted_dates]
    global_pace_list = [global_pace_timeseries[d] for d in sorted_dates]
    expected_pace_list = [expected_pace[d] for d in sorted_dates]

    
    #Use the quantile to determine the threshold
    sorted_mahal = sorted(mahal_list)
    threshold = getQuantile(sorted_mahal, threshold_quant)
    
    
    # The symbols array contains "1" if there is an outlier, "0" if there is not
    symbols = []
    for i in range(len(mahal_list)):
        if(mahal_list[i] > threshold or c_list[i]==1):
            symbols.append(1)
        else:
            symbols.append(0)
    
    
    # Set up the hidden markov model.  We are modeling the non-event states as "0"
    # and event states as "1"
    
    # Transition matrix with heavy weight on the diagonals ensures that the model
    # is likely to stick in the same state rather than rapidly switching.  In other
    # words, the predictions will be relatively "smooth"
    trans_matrix = array([[.95, .05],
                      [.05,.95]])

    # Emission matrix - state 0 is likely to emit symbol 0, and vice versa
    # In other words, events are likely to be outliers
    emission_matrix = array([[.95, .05],
                          [.05,.95]])
    
    # Actually set up the hmm
    model = MultinomialHMM(n_components=2, transmat=trans_matrix)
    model.emissionprob_ = emission_matrix
    
    # Make the predictions
    lnl, predictions = model.decode(symbols)
    