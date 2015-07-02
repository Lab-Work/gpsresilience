# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 09:00:30 2015

@author: Brian Donovan (briandonovan100@gmail.com)
"""

from numpy import random, array,transpose, median, mean, var
import numpy as np
from numpy.linalg import eig

from datetime import datetime, timedelta
from multiprocessing import Pool
from functools import partial
import csv
from collections import defaultdict

from measureOutliers import readGlobalPace
from hmm_event_detection import detect_events_hmm, readOutlierScores, augment_outlier_scores
from tools import logMsg, DefaultPool


events_data = [("Snowstorm1" , "2010-12-26 13:00:00" , 137),
("Sandy" , "2012-10-28 21:00:00" , 116),
("?1" , "2012-11-12 07:00:00" , 110),
("Snowstorm2" , "2011-01-31 09:00:00" , 103),
("Snowstorm3" , "2011-01-26 09:00:00" , 56),
("Protest?" , "2011-09-18 19:00:00" , 49),
("Irene" , "2011-08-27 11:00:00" , 46),
("Thanksgiving" , "2011-11-22 11:00:00" , 43),
("?2" , "2013-10-12 01:00:00" , 43),
("?3" , "2013-09-28 08:00:00" , 37)]

reference_events = []
for event in events_data:
    (name, date_str, duration) = event
    start_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    end_date = start_date + timedelta(hours=duration)
    reference_events.append((name, start_date, end_date, duration))


def match_events(events):
    event_durations={}
    event_starts={}
    event_ends={}
    event_max_pace_devs={}
    event_min_pace_devs={}
    for event in reference_events:
        event_durations[event] = 0
        event_starts[event]='?'
        event_ends[event] = '?'
        event_max_pace_devs[event] = '?'
        event_min_pace_devs[event] = '?'
        
    for event in reference_events:
        (ev_name, ev_start, ev_end, ev_duration) = event

        for [start_date, end_date, duration, max_mahal, max_pace_dev, min_pace_dev] in events:
            #start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            #end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            duration = (end_date - start_date).total_seconds() / 3600 + 1
        
        
            if(ev_end > start_date and ev_start < end_date):
                #print ("MATCH - %d , %s --> %s" % (duration, str(start_date), str(end_date)))
                if(event not in event_durations or duration > event_durations[event]):
                    event_durations[event] = duration
                    event_starts[event] = start_date
                    event_ends[event] = end_date
                    event_max_pace_devs[event] = max_pace_dev
                    event_min_pace_devs[event] = min_pace_dev

    chunk = []
    for event in event_durations:
        (name,_,_,_) = event
        this_event = [name, event_starts[event], event_ends[event],
                      event_durations[event], event_max_pace_devs[event],
                      event_min_pace_devs[event]]
        chunk.append(this_event)
        

        
    return chunk
            




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
        w.writerow(['event','start_date', 'end_date', 'duration', 'max_pace_dev', 'min_pace_dev'])
        for chunk in result:
            w.writerows(chunk)

def run_random_sims(outlier_score_file, feature_dir):
    
    mahal_timeseries, c_timeseries = readOutlierScores(outlier_score_file)
    global_pace_timeseries = readGlobalPace(feature_dir)
    
    for p in range(50):
        print ("Sim %d" % p)
        initial_state, trans_matrix, emission_matrix = randomly_draw_parameters()
    
        events, predictions = detect_events_hmm(mahal_timeseries, c_timeseries,
                        global_pace_timeseries, threshold_quant=.95,
                        trans_matrix = trans_matrix,
                      emission_matrix=emission_matrix)
        new_scores_file = 'tmp_results/coarse_events_k%d_scores.csv'%p
    
        augment_outlier_scores(outlier_score_file, new_scores_file, predictions)






def approx_beta_median(alpha, beta, num_guesses=10000000):
    vals = [random.beta(alpha, beta) for x in xrange(num_guesses)]
    return median(vals)
    




def test_median():
    alpha,beta =  beta_method_of_moments(.99, .03)
    print alpha, beta, approx_beta_median(alpha, beta)
    
    alpha,beta = beta_method_of_moments(.95, .05)
    print alpha, beta, approx_beta_median(alpha, beta)
    
    alpha,beta = beta_method_of_moments(.6, .05)
    print alpha, beta, approx_beta_median(alpha, beta)



def find_most_common_event_durations(in_filename, out_filename):
    event_duration_counts = {}
    event_lookup = {}
    
    with open(in_filename, 'r') as f:
        r = csv.reader(f)
        r.next()
        for (event, start_date, end_date, duration, max_pace_dev, min_pace_dev) in r:
            if(event not in event_duration_counts):
                event_duration_counts[event] = defaultdict(int)
                event_lookup[event] = {}
            event_duration_counts[event][duration] += 1
            event_lookup[event][duration] = (event, start_date, end_date, int(float(duration)), max_pace_dev, min_pace_dev)
            
    events = []
    for event in event_duration_counts:
        best_duration = 0
        highest_count = -1
        for duration in event_duration_counts[event]:
            if(event_duration_counts[event][duration] > highest_count):
                highest_count = event_duration_counts[event][duration]
                best_duration = duration
        
        events.append(event_lookup[event][best_duration])
    
    events.sort(key= lambda x: x[3], reverse=True)
    
    with open(out_filename, 'w') as f:
        w = csv.writer(f)
        w.writerow(['event', 'start_date', 'end_date', 'duration', 'max_pace_dev', 'min_pace_dev'])
        w.writerows(events)        




if(__name__=="__main__"):
    
    find_most_common_event_durations('results/coarse_montecarlo.csv', 'results/coarse_events_consensus.csv')
    find_most_common_event_durations('results/fine_montecarlo.csv', 'results/fine_events_consensus.csv')
    
    
    if(False):
        run_random_sims('results/coarse_features_imb20_k10_RPCAtune_10000000pcs_5percmiss_robust_outlier_scores.csv','4year_features')
        test_median()
        
        print beta_method_of_moments(.99, .03)
        print beta_method_of_moments(.95, .05)
        print beta_method_of_moments(.6, .05)
    

    
    
    if(False):
        logMsg("Starting")
        run_sims_in_parallel('results/coarse_features_imb20_k10_RPCAtune_10000000pcs_5percmiss_robust_outlier_scores.csv',
                             '4year_features', 'results/coarse_montecarlo.csv')
        
        logMsg("Finished OD method")
        run_sims_in_parallel('results/link_features_imb20_k10_RPCAtune_10000000pcs_5percmiss_robust_outlier_scores.csv',
                             '4year_features', 'results/fine_montecarlo.csv')
        logMsg("Finished link-level method")