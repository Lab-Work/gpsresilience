# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 15:44:37 2015

@author: Brian Donovan (briandonovan100@gmail.com)

This module contains functions which help choose the gamma and tolerance values for
RPCA - these are inputs to op_modified.opursuit().
"""

from tools import *
from numpy import  square
from numpy import column_stack, arange
import numpy as np

from data_preprocessing import remove_bad_dimensions_grouped
from op_modified import opursuit, obj_func



from random import uniform, normalvariate
from scipy.stats import norm


import csv
from sys import stdout
from multiprocessing import Pool

from measureLinkOutliers import load_pace_data, load_from_file
from measureOutliers import readPaceData

class ConvergenceException:
    def __init__(self, num_guesses):
        self.num_guesses = num_guesses
    pass


def fast_rank(A):
    u, s, v = np.linalg.svd(A)
    rank = np.sum(s > .0001)
    return rank




# Helper method for tuning gamma and tolerance. Guesses a new value for a parameter,
# given a low bound and a high bound
# Params:
    # current_val - the current value of the parameter
    # lo_bound - an approximate lower bound, it is unlikely to generate a value lower than this
    # hi_bound - an approximate upper bound, it is unlikely to generate a value higher than this
    # SEARCH_RATE - if one of the bounds are missing, guesses will extend in that direction
        # at a rate proportional to this
    # BACKTRACK_PROB - the probability of generating a point outside of the bounds
def guess_param(current_val, lo_bound, hi_bound, SEARCH_RATE=5, BACKTRACK_PROB=.1):
    lo_val = lo_bound
    hi_val = hi_bound

    # If we are missing either of the bounds, artificially create them using the search rate
    if(lo_val==None):
        #lo_val = current_val / SEARCH_RATE
        if(hi_val!=None):
            lo_val = hi_val / SEARCH_RATE
        else:
            lo_val = current_val / SEARCH_RATE
    if(hi_val==None):
        #hi_val = current_val * SEARCH_RATE
        if(lo_val!=None):
            hi_val = lo_val * SEARCH_RATE
        else:
            hi_val = current_val * SEARCH_RATE
    
    # Create a normal distribution centered between the two bounds, and
    # Ensure that there is only a BACKTRACK_PROB probability of generating
    # a point outside of that range
    mean = (hi_val+ lo_val) / 2
    (lo_conf_bound, hi_conf_bound) = norm.interval(1 - BACKTRACK_PROB)
    sd = (hi_val - lo_val) / (hi_conf_bound*2)
    
    # Draw a random guess from the distribution and update bounds if necessary
    current_val = normalvariate(mean, sd)
    current_val = max(current_val, .0001)
    if(lo_bound!=None):
        lo_bound = min(lo_bound, current_val)
    if(hi_bound!=None):
        hi_bound = max(hi_bound, current_val)
    
    
    return current_val, lo_bound, hi_bound
        
        
        
        
        




# Helper method for increasing_tolerance_search (this is where most of the heavy
# lifting is done).  Uses a randomized bisection technique to choose gamma and tol
# in such a way that the number of outliers in the C matrix and the rank of the L
# matrix meet some target values
# Params:
    # vectors - The data to perform RPCA on, a list of Numpy column vectors
    # gamma_guess - an intial guess for gamma
    # tol_guess - an initial guess for the tolerance
    # lo_target_c_perc - lower bound for the desired percentage of outliers
    # hi_target_c_perc - upper bound for the desired percentage of otuliers
    # lo_Target_num_pcs - lower bound for the desired rank of the data
    # hi_target_num_pcs - upper bound for the desired rank of the data
def tune_gamma_and_tol(vectors, gamma_guess=.5, tol_guess=1e-2,
                        lo_target_c_perc=.04, hi_target_c_perc = .10,
                        lo_target_num_pcs=10, hi_target_num_pcs = 15):
                            

    BACKTRACK_PROB=.0000001
    MAX_NUM_RESETS = 5
    num_resets = 0

    
    data_matrix = column_stack(vectors)
    O = (data_matrix!=0)*1 # Observation matrix - 1 where we have data, 0 where we do not

    #Initially, we don't have any bounds on our search
    lo_gamma = None
    hi_gamma = None
    gamma = gamma_guess
    
    lo_tol = None
    hi_tol = None
    tol_perc = tol_guess
    
    num_guesses = 0
    while(True):
        num_guesses += 1
        logMsg("BS: Trying gamma=%f, tol=%f" % (gamma, tol_perc))
        
        try:
            L,C,term,n_iter = opursuit(data_matrix, O, gamma, tol_perc=tol_perc, eps_ratio=20)
        
            
            
            #centered_L = scale_and_center(L, scale=False)
            #pcs, robust_lowdim_data = pca(centered_L, 100000)
            num_pca_dimensions = fast_rank(L)
            
            #otherrank = fast_rank(L)
            #print ("RANK %d , %d" % (num_pca_dimensions, otherrank))
            
            c_vals = [(sum(square(C[:,i]))!=0)*1 for i in  xrange(C.shape[1])]
            c_perc = float(sum(c_vals)) / len(c_vals)
            
            logMsg(">>>>>> pcs=%d, outliers=%f" % (num_pca_dimensions, c_perc))
            
            
            # If we have found acceptable values, stop
            if(c_perc >= lo_target_c_perc and c_perc <= hi_target_c_perc
                and num_pca_dimensions >= lo_target_num_pcs
                and num_pca_dimensions <= hi_target_num_pcs):
                break
            
            # Otherwise, use our target values to figure out if we need to increase/decrease
            # gamma or tol
            
            if(num_pca_dimensions >= lo_target_num_pcs and c_perc >= lo_target_c_perc):
                print("#rank too high and too many outliers - increase tolerance")
                lo_tol = tol_perc
            elif(num_pca_dimensions >= lo_target_num_pcs and c_perc <= lo_target_c_perc):
                print("#rank too high and too few outliers - decrease gamma")
                hi_gamma = gamma
            elif(num_pca_dimensions <= lo_target_num_pcs and c_perc >= lo_target_c_perc):
                print("#rank too low and too many outliers - increase gamma")
                lo_gamma = gamma
            elif(num_pca_dimensions <= lo_target_num_pcs and c_perc <= lo_target_c_perc):
                print("#rank too low and too few outliers - decrease tolerance")
                hi_tol = tol_perc
    
            
            (gamma, lo_gamma, hi_gamma) = guess_param(gamma, lo_gamma, hi_gamma,
                                            SEARCH_RATE=2, BACKTRACK_PROB=BACKTRACK_PROB)
            (tol_perc, lo_tol, hi_tol) = guess_param(tol_perc, lo_tol, hi_tol,
                                            SEARCH_RATE=5, BACKTRACK_PROB=BACKTRACK_PROB)
            
    
            print("%s < gamma < %s  ,  %s < tol < %s" % tuple(map(str, [lo_gamma, hi_gamma, lo_tol,hi_tol])))

        except Exception as e:
            logMsg(e.message)
            lo_tol = .01
            hi_tol = .01
        
        
        if( (lo_tol !=None and hi_tol != None and hi_tol/lo_tol > .99 and hi_tol/lo_tol < 1.01)
            or (lo_gamma !=None and hi_gamma != None and hi_gamma/lo_gamma > .99 and hi_gamma/lo_gamma < 1.01)):
            print("----------------Got stuck")
            BACKTRACK_PROB = .3
            num_resets += 1
            
            if(num_resets > MAX_NUM_RESETS):
                raise ConvergenceException(num_guesses)
            else:
                
                hi_gamma = None
                lo_gamma = None
                hi_tol = None
                lo_tol = None
                
                gamma *= (2**uniform(-1,1))
                tol_perc *= (10**uniform(-1,1))
        
    
    print obj_func(L,C,gamma)
    return gamma, tol_perc, num_guesses, L, C


# Searches for values of gamma and tol such that the number of outliers is between
# 5% and 10%, and that the rank of the data is between 10 and 15.  The rank bounds
# are increased if lower values fail
# Params:
    # vectors - the data to perform RPCA on. A list of Numpy column vectors
def increasing_tolerance_search(vectors):
    
    hi_num_pcs = 15
    num_guesses = 0
    while(True):
        try:
            gamma, tol, part_num_guesses, L, C = tune_gamma_and_tol(vectors,
                                gamma_guess=1.0, tol_guess=1e-3,
                                lo_target_c_perc=.05, hi_target_c_perc = .10,
                                lo_target_num_pcs=10, hi_target_num_pcs = hi_num_pcs)
            

            num_guesses += part_num_guesses
            break
        except ConvergenceException as e:
            num_guesses += e.num_guesses
            logMsg(" -------------------- Relaxing Condition ------------------------- ")
            hi_num_pcs += 5
    
    return gamma, tol, num_guesses, hi_num_pcs, L, C
    
            
    


###############################################################################3
# Everything below this line is for testing purposes


def paramIterator(data_matrix, O):
    #tols = [1e-06, 5e-06, 1e-05, 5e-05, 1e-04, 5e-04, 1e-03, 5e-03]
    tols = arange(.001, .005, .0001)
    gammas = arange(.3,1.1,.01)
    
    for tol_perc in tols:
            for gamma in gammas:
                yield (data_matrix, O, tol_perc, gamma)



def tryParameters((data_matrix, O, tol_perc, gamma)):
    logMsg("Trying tol=%f, gamma=%f" % (tol_perc, gamma))
    L,C,term,n_iter = opursuit(data_matrix, O, gamma, tol_perc=tol_perc, eps_ratio=10)
    c_vals = [(sum(square(C[:,i]))!=0)*1 for i in  xrange(C.shape[1])]
    c_perc = float(sum(c_vals)) / len(c_vals)
    centered_L = scale_and_center(L, scale=False)
    pcs, robust_lowdim_data = pca(centered_L, 100000)
    num_pca_dimensions = pcs.shape[1]
    
    print([tol_perc, gamma, c_perc, num_pca_dimensions, n_iter])
    return [tol_perc, gamma, c_perc, num_pca_dimensions, n_iter]



def sweepGammaAndTol(vectors, pool=DefaultPool()):
    data_matrix = column_stack(vectors)
    O = (data_matrix!=0)*1 # Observation matrix - 1 where we have data, 0 where we do not
    
    it = paramIterator(data_matrix, O)
    vals = pool.map(tryParameters, it)
    

    
    
    with open('param_sweep.csv', 'w') as f:
        w = csv.writer(f)
        w.writerow(['tol','gamma','outliers','rank', 'iter'])
        for val in vals:
            w.writerow(val)
    
    print("Done")



def compare_eps(vectors):
    data_matrix = column_stack(vectors)
    O = (data_matrix!=0)*1 # Observation matrix - 1 where we have data, 0 where we do not
    
    
    gamma = .5
    tol_perc = .002
    tol_perc = .00000001
    for e in [2,5,10,20,50,100]:
        L,C,term,n_iter = opursuit(data_matrix, O, gamma, tol_perc=tol_perc, eps_ratio=e)
        obj = obj_func(L,C,gamma)
        c_vals = [(sum(square(C[:,i]))!=0)*1 for i in  xrange(C.shape[1])]
        c_perc = float(sum(c_vals)) / len(c_vals)
        centered_L = scale_and_center(L, scale=False)
        pcs, robust_lowdim_data = pca(centered_L, 100000)
        num_pca_dimensions = pcs.shape[1]
        print "eps=%d term=%f n_iter=%d obj=%f rank=%d c_perc=%f" % (e,term, n_iter, obj, num_pca_dimensions, c_perc)
        


    

if( __name__=="__main__"):
    pool = Pool(2)
    #pool = DefaultPool()
    #use_link_db = 'tmp_vectors_Monday_12.pickle'
    use_link_db=False    
    inDir = "features_imb20_k10"
    
    if(use_link_db):
        pace_timeseries, pace_grouped, weights_grouped, dates_grouped, trip_names, consistent_link_set = load_from_file(use_link_db)
    else:
        (pace_timeseries, pace_grouped, dates_grouped, trip_names) = readPaceData(inDir)
    
    pace_grouped = remove_bad_dimensions_grouped(pace_grouped, .05)
    
    #vectors = pace_grouped[('Tuesday', 22)]
    # ('Tuesday', 12)
    # ('Friday', 0)
    #sweepGammaAndTol(vectors, pool)   
    #quit()
    
    
    key = pace_grouped.keys()[1]
    for key in pace_grouped:
        #key = ('Wednesday', 23)
        #sweepGammaAndTol(pace_grouped[key], pool)
        print("**************************************")
        print key
        increasing_tolerance_search(pace_grouped[key])
        #compare_eps(pace_grouped[key])
        print
        print
    
    pool.close()

