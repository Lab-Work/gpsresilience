# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 09:00:30 2015

@author: Brian Donovan (briandonovan100@gmail.com)
"""

from numpy import random, array,transpose
import numpy as np
from numpy.linalg import eig

from datetime import datetime, timedelta
from multiprocessing import Pool
from functools import partial
import csv

from measureOutliers import readGlobalPace
from hmm_event_detection import detect_events_hmm, readOutlierScores
from tools import logMsg


events_data = [("Snowstorm" , "2010-12-26 13:00:00" , 137),
("Sandy" , "2012-10-28 21:00:00" , 116),
("?" , "2012-11-12 07:00:00" , 110),
("Snowstorm" , "2011-01-31 09:00:00" , 103),
("Snowstorm" , "2011-01-26 09:00:00" , 56),
("Protest?" , "2011-09-18 19:00:00" , 49),
("Irene" , "2011-08-27 11:00:00" , 46),
("Thanksgiving" , "2011-11-22 11:00:00" , 43),
("?" , "2013-10-12 01:00:00" , 43),
("?" , "2013-09-28 08:00:00" , 37)]

reference_events = []
for event in events_data:
    (name, date_str, duration) = event
    start_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    end_date = start_date + timedelta(hours=duration)
    reference_events.append((name, start_date, end_date, duration))


def match_events(events):
    event_durations={}
    for event in reference_events:
        event_durations[event] = 0
        
    for event in reference_events:
        (ev_name, ev_start, ev_end, ev_duration) = event

        for [start_date, end_date, duration, max_mahal, max_pace_dev, min_pace_dev] in events:
            #start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            #end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            duration = (end_date - start_date).total_seconds() / 3600 + 1
        
        
            if(ev_end > start_date and ev_start < end_date):
                #print ("MATCH - %d , %s --> %s" % (duration, str(start_date), str(end_date)))
                event_durations[event] = max(event_durations[event], duration)
        
    return [["%s %s" % (name, str(start_date)), event_durations[name,start_date,end_date,dur]] for (name, start_date,end_date,dur) in event_durations]
            




def sorted_eig(m):
    evals, evects = eig(m)
    sort_order = evals.argsort()[::-1]
    evals = np.sort(evals)[::-1]
    evects = evects[:,sort_order]
    return evals, evects



def beta_method_of_moments(mean, sd):
    v = sd**2
    
    alpha = mean * (mean * (1 - mean)/v - 1)
    beta = (1 - mean) * (mean*(1-mean) / v - 1)
    return (alpha, beta)


def randomly_draw_parameters(state_remain_mean=.99, state_remain_sd=.03,
                   normal_emission_mean=.95, normal_emission_sd=.05,
                   event_emission_mean=.6, event_emission_sd=.05):
                   
    alpha, beta = beta_method_of_moments(state_remain_mean, state_remain_sd)
    a1 = random.beta(alpha, beta)
    a2 = random.beta(alpha, beta)
    trans_matrix = array(([[a1, 1-a1],
                            [1-a2, a2]]))
    
    # The initial state is the steady state of the transition matrix
    # which is computed via the leading eigenvector
    w, v =sorted_eig(transpose(trans_matrix))
    initial_state = v[:,0]
    initial_state /= sum(initial_state)

    
    
    
    alpha, beta = beta_method_of_moments(normal_emission_mean, normal_emission_sd)
    a1 = random.beta(alpha, beta)
    
    alpha, beta = beta_method_of_moments(event_emission_mean, event_emission_sd)
    a2 = random.beta(alpha, beta)


    # Emission matrix - state 0 is likely to emit symbol 0, and vice versa
    # In other words, events are likely to be outliers
    emission_matrix = array(([[a1, 1-a1],
                            [1-a2, a2]]))
    
    return initial_state, trans_matrix, emission_matrix






def run_one_simulation(mahal_timeseries, c_timeseries, global_pace_timeseries):
    initial_state, trans_matrix, emission_matrix = randomly_draw_parameters()
    
    events, predictions = detect_events_hmm(mahal_timeseries, c_timeseries,
                        global_pace_timeseries, threshold_quant=.95,
                        trans_matrix = trans_matrix,
                      emission_matrix=emission_matrix)
    
    return match_events(events)
    

def run_many_simulations(num, mahal_timeseries=None , c_timeseries=None, global_pace_timeseries=None):
    return [event for i in xrange(num)
            for event in run_one_simulation(mahal_timeseries, c_timeseries, global_pace_timeseries)]


def run_sims_in_parallel(outlier_score_file, feature_dir, output_file):
    pool = Pool(8)
    
    mahal_timeseries, c_timeseries = readOutlierScores(outlier_score_file)
    global_pace_timeseries = readGlobalPace(feature_dir)
    
    sim_function = partial(run_many_simulations, mahal_timeseries = mahal_timeseries,
                           c_timeseries = c_timeseries, global_pace_timeseries=global_pace_timeseries)
    sim_sizes = [1250]*8
    result = pool.map(sim_function, sim_sizes)
    
    with open(output_file, 'w') as f:
        w = csv.writer(f)
        w.writerow(['event','duration'])
        for chunk in result:
            w.writerows(chunk)
                
    

if(__name__=="__main__"):
    logMsg("Starting")
    run_sims_in_parallel('results/coarse_features_imb20_k10_RPCAtune_10000000pcs_5percmiss_robust_outlier_scores.csv',
                         '4year_features', 'results/coarse_montecarlo.csv')
    
    logMsg("Finished OD method")
    run_sims_in_parallel('results/link_features_imb20_k10_RPCAtune_10000000pcs_5percmiss_robust_outlier_scores.csv',
                         '4year_features', 'results/fine_montecarlo.csv')
    logMsg("Finished link-level method")