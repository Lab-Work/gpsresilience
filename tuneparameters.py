# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 15:44:37 2015

@author: Brian Donovan (briandonovan100@gmail.com)
"""

from tools import *
from numpy import  square
from numpy import column_stack, arange

from data_preprocessing import pca, scale_and_center
from pyrpca_core.op import opursuit



from random import random


import csv
from sys import stdout
from multiprocessing import Pool

from measureLinkOutliers import load_pace_data, load_from_file
from measureOutliers import readPaceData




def lowdim_mahalanobis_distance(pcs, robust_lowdim_data, centered_corrupt, keep_dims):
    new_pcs = pcs[:,0:keep_dims]
    new_rld = robust_lowdim_data[0:keep_dims,:]
    
    
    vects = [new_rld[:,i] for i in xrange(new_rld.shape[1])]
    stats = IndependentGroupedStats(vects) # Diagonal covariance assumption is valid since we did PCA
    
    corrupt_lowdim_data = new_pcs.transpose() * centered_corrupt
    vects = [corrupt_lowdim_data[:,i] for i in xrange(corrupt_lowdim_data.shape[1])]
    mahals = [stats.mahalanobisDistance(vect) for vect in vects]
    
    return mahals






def tuneGamma(vectors, tol_perc, gamma_guess=.5, target_c_perc=.10):
    data_matrix = column_stack(vectors)
    O = (data_matrix!=0)*1 # Observation matrix - 1 where we have data, 0 where we do not
        
         
    SEARCH_RATE = 1.2
    TOLERANCE = .01
    
    #Initially, we don't have any bounds on our search
    lo_gamma = None
    hi_gamma = None
    gamma = gamma_guess
    num_guesses = 0
    while(True):
        
        
        #logMsg("BS: Trying gamma=%f" % gamma)
        
        # Use outlier pursuit to detect outliers
        L,C,term,n_iter = opursuit(data_matrix, O, gamma, tol_perc=tol_perc)
        c_vals = [(sum(square(C[:,i]))!=0)*1 for i in  xrange(C.shape[1])]
        
        c_perc = float(sum(c_vals)) / len(c_vals)
        #logMsg("BS: Fraction of outliers: %f" % c_perc)
        num_guesses += 1
        
        # If we have found an acceptable gamma value, then stop
        if(c_perc > target_c_perc - TOLERANCE and c_perc < target_c_perc + TOLERANCE):
            break
        
        if(hi_gamma != None and lo_gamma != None and hi_gamma / lo_gamma < 1.00001):
            break
        
        # Otherwise, update gamma and try again
        if(c_perc < target_c_perc):
            #logMsg("BS: Decreasing gamma")
            # Don't have enough outliers - decrease gamma
            hi_gamma = gamma
            if(lo_gamma==None):
                gamma /= SEARCH_RATE
            else:
                gamma = (hi_gamma + lo_gamma) / 2
        else:
            #logMsg("BS: Increasing gamma")
            # Have too many outliers - increase gamma
            lo_gamma = gamma
            if(hi_gamma==None):
                gamma *= SEARCH_RATE
            else:
                gamma = (hi_gamma + lo_gamma) / 2
        
        #logMsg("BS: %s < gamma < %s" % (str(lo_gamma), str(hi_gamma)))
        stdout.flush()
    
    logMsg ("BS: Chose gamma=%f , fraction of outliers=%f after %d attempts" % (gamma, c_perc, num_guesses))
    return gamma,L,C




def tuneTol(vectors, gamma=.5, tol_guess=10e-3, target_num_pcs=10):
    data_matrix = column_stack(vectors)
    O = (data_matrix!=0)*1 # Observation matrix - 1 where we have data, 0 where we do not
    
    SEARCH_RATE = 10
    tol_perc = tol_guess
    lo_tol = None
    hi_tol = None
    
    while(True):
        logMsg("****** Trying tolerance=%f" % tol_perc)
        L,C,term,n_iter = opursuit(data_matrix, O, gamma, tol_perc=tol_perc)
        #L,C = tuneGamma(vectors, tol_perc, gamma_guess=gamma, target_c_perc=target_c_perc)
        centered_L = scale_and_center(L, scale=False)
        pcs, robust_lowdim_data = pca(centered_L, 100000)
        num_pca_dimensions = pcs.shape[1]
        logMsg("****** Num eigenvalues : %d" % num_pca_dimensions)
        
        if(num_pca_dimensions==target_num_pcs):
            break
        
        
        if(hi_tol!=None and lo_tol!=None and hi_tol/lo_tol < 1.0001):
            logMsg("  I GOT STUCK ")
            hi_tol = None
            lo_tol = None
            tol_perc *= 10**(2*random() - 1)
            continue
        
        
        if(num_pca_dimensions < target_num_pcs):
            logMsg("BS: Decreasing tolerance")
            # Don't have enough outliers - decrease gamma
            hi_tol = tol_perc
            if(lo_tol==None):
                tol_perc /= SEARCH_RATE
            else:
                tol_perc = (hi_tol + lo_tol) / 2
        else:
            logMsg("BS: Increasing tolerance")
            # Have too many outliers - increase gamma
            lo_tol = tol_perc
            if(hi_tol==None):
                tol_perc *= SEARCH_RATE
            else:
                tol_perc = (hi_tol + lo_tol) / 2
        
        stdout.flush()
    
    return tol_perc, L, C






def tuneGammaAndTol(vectors, gamma_guess=.5, tol_guess=10e-3, target_c_perc=.05, target_num_pcs=10):
    SEARCH_RATE = 10
    gamma = gamma_guess
    tol_perc = tol_guess
    lo_tol = None
    hi_tol = None
    
    while(True):
        logMsg("****** Trying tolerance=%f" % tol_perc)
        gamma,L,C = tuneGamma(vectors, tol_perc, gamma_guess=gamma, target_c_perc=target_c_perc)
        centered_L = scale_and_center(L, scale=False)
        pcs, robust_lowdim_data = pca(centered_L, 100000)
        num_pca_dimensions = pcs.shape[1]
        logMsg("****** Num eigenvalues : %d" % num_pca_dimensions)
        
        if(num_pca_dimensions==target_num_pcs):
            break
        
        
        if(hi_tol!=None and lo_tol!=None and hi_tol/lo_tol < 1.0001):
            logMsg("  I GOT STUCK ")
            hi_tol = None
            lo_tol = None
            tol_perc *= 10**(2*random() - 1)
            continue
        
        
        if(num_pca_dimensions < target_num_pcs):
            logMsg("BS: Decreasing tolerance")
            # Don't have enough outliers - decrease gamma
            hi_tol = tol_perc
            if(lo_tol==None):
                tol_perc /= SEARCH_RATE
            else:
                tol_perc = (hi_tol + lo_tol) / 2
        else:
            logMsg("BS: Increasing tolerance")
            # Have too many outliers - increase gamma
            lo_tol = tol_perc
            if(hi_tol==None):
                tol_perc *= SEARCH_RATE
            else:
                tol_perc = (hi_tol + lo_tol) / 2
        
        stdout.flush()
    
    return tol_perc, gamma, L, C
        


def tuneGammaAndTol2(vectors, gamma_guess=.3, tol_guess=10e-3, target_c_perc=.05, target_num_pcs=10):
    #data_matrix = column_stack(vectors)
    #O = (data_matrix!=0)*1 # Observation matrix - 1 where we have data, 0 where we do not
        
         
    SEARCH_RATE = 1.2
    TOLERANCE = .01
    
    #Initially, we don't have any bounds on our search
    lo_gamma = None
    hi_gamma = None
    gamma = gamma_guess
    num_guesses = 0
    tol_perc = tol_guess
    while(True):
        
        
        #logMsg("BS: Trying gamma=%f" % gamma)
        
        # Use outlier pursuit to detect outliers
        # L,C,term,n_iter = opursuit(data_matrix, O, gamma, tol_perc=tol_perc)
        tol_perc, L, C = tuneTol(vectors, gamma=gamma, tol_guess=tol_perc, target_num_pcs=10) 
       
        c_vals = [(sum(square(C[:,i]))!=0)*1 for i in  xrange(C.shape[1])]
        
        c_perc = float(sum(c_vals)) / len(c_vals)
        #logMsg("BS: Fraction of outliers: %f" % c_perc)
        num_guesses += 1
        
        # If we have found an acceptable gamma value, then stop
        if(c_perc > target_c_perc - TOLERANCE and c_perc < target_c_perc + TOLERANCE):
            break
        
        if(hi_gamma != None and lo_gamma != None and hi_gamma / lo_gamma < 1.00001):
            break
        
        # Otherwise, update gamma and try again
        if(c_perc < target_c_perc):
            #logMsg("BS: Decreasing gamma")
            # Don't have enough outliers - decrease gamma
            hi_gamma = gamma
            if(lo_gamma==None):
                gamma /= SEARCH_RATE
            else:
                gamma = (hi_gamma + lo_gamma) / 2
        else:
            #logMsg("BS: Increasing gamma")
            # Have too many outliers - increase gamma
            lo_gamma = gamma
            if(hi_gamma==None):
                gamma *= SEARCH_RATE
            else:
                gamma = (hi_gamma + lo_gamma) / 2
        
        #logMsg("BS: %s < gamma < %s" % (str(lo_gamma), str(hi_gamma)))
        stdout.flush()
    
    logMsg ("BS: Chose gamma=%f , fraction of outliers=%f after %d attempts" % (gamma, c_perc, num_guesses))
    return gamma,L,C



def paramIterator(data_matrix, O):
    tols = [1e-06, 5e-06, 1e-05, 5e-05, 1e-04, 5e-04, 1e-03, 5e-03]
    gammas = arange(.3,1.1,.01)
    
    for tol_perc in tols:
            for gamma in gammas:
                yield (data_matrix, O, tol_perc, gamma)



def tryParameters((data_matrix, O, tol_perc, gamma)):
    logMsg("Trying tol=%f, gamma=%f" % (tol_perc, gamma))
    L,C,term,n_iter = opursuit(data_matrix, O, gamma, tol_perc=tol_perc)
    c_vals = [(sum(square(C[:,i]))!=0)*1 for i in  xrange(C.shape[1])]
    c_perc = float(sum(c_vals)) / len(c_vals)
    centered_L = scale_and_center(L, scale=False)
    pcs, robust_lowdim_data = pca(centered_L, 100000)
    num_pca_dimensions = pcs.shape[1]
    
    print([tol_perc, gamma, c_perc, num_pca_dimensions])
    return [tol_perc, gamma, c_perc, num_pca_dimensions]



def sweepGammaAndTol(vectors, pool=DefaultPool()):
    data_matrix = column_stack(vectors)
    O = (data_matrix!=0)*1 # Observation matrix - 1 where we have data, 0 where we do not
    
    it = paramIterator(data_matrix, O)
    vals = pool.map(tryParameters, it)
    

    
    
    with open('param_sweep.csv', 'w') as f:
        w = csv.writer(f)
        w.writerow(['tol','gamma','outliers','rank'])
        for val in vals:
            w.writerow(val)
    
    print("Done")
    
    

if( __name__=="__main__"):
    pool = Pool(8)
    #pool = DefaultPool()
    use_link_db = 'tmp_vectors_Monday_12.pickle'
    inDir = "features_imb20_k10"
    
    if(use_link_db):
        pace_timeseries, pace_grouped, weights_grouped, dates_grouped, trip_names, consistent_link_set = load_from_file(use_link_db)
    else:
        (pace_timeseries, pace_grouped, dates_grouped, trip_names) = readPaceData(inDir)
    
    key = pace_grouped.keys()[0]
    
    sweepGammaAndTol(pace_grouped[key], pool)
    pool.close()

