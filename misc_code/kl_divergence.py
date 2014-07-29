# -*- coding: utf-8 -*-
"""
Created on Wed May 21 17:37:25 2014

@author: brian
"""
import numpy
from numpy import matrix, transpose, mean, shape
from numpy.linalg import inv, det
from math import log
import os, csv
from collections import defaultdict

from cov_matrix import *
from tools import *

class MyException(Exception):
	pass

def readPaceData(dirName):
	paceFileName = os.path.join(dirName, "pace_features.csv")
	paceVarFileName = os.path.join(dirName, "pace_var_features.csv")	
	countFileName = os.path.join(dirName, "count_features.csv")
	
	#Read the pace file
	r = csv.reader(open(paceFileName, "r"))
	colIds = getHeaderIds(r.next())
	
	pace_timeseries = {}
	pace_grouped = defaultdict(list)
	var_timeseries = {}
	count_timeseries = {}
		
	
	for line in r:
		#Extract info
		#First 3 columns
		date = line[colIds["Date"]]
		hour = int(line[colIds["Hour"]])
		weekday = line[colIds["Weekday"]]
		#Last 16 columns
		paces = map(float, line[colIds["E-E"]:])
		
		#Convert to numpy column vector
		v = transpose(matrix(paces))
		#Save vector in the timeseries and the group
		pace_timeseries[(date, hour, weekday)] = v
		
		if(allNonzero(v)):
			pace_grouped[(weekday, hour)].append(v)

	
	
	#Read pace variance file

	r = csv.reader(open(paceVarFileName, "r"))
	colIds = getHeaderIds(r.next())

	
	for line in r:
		#Extract info
		#First 3 columns
		date = line[colIds["Date"]]
		hour = int(line[colIds["Hour"]])
		weekday = line[colIds["Weekday"]]
		#Last 16 columns
		paces = map(float, line[colIds["E-E"]:])
		
		#Convert to numpy column vector
		v = transpose(matrix(paces))
		#Save vector in the timeseries
		var_timeseries[(date, hour, weekday)] = v
	
	#Read the trip count file	
	r = csv.reader(open(countFileName, "r"))
	colIds = getHeaderIds(r.next())
	for line in r:
		#Extract info
		#First 3 columns
		date = line[colIds["Date"]]
		hour = int(line[colIds["Hour"]])
		weekday = line[colIds["Weekday"]]
		#Last 16 columns
		counts = map(float, line[colIds["E-E"]:])
		
		#Convert to numpy column vector
		v = transpose(matrix(counts))
		#Save vector in the timeseries
		count_timeseries[(date, hour, weekday)] = v
		
	return (pace_timeseries, var_timeseries, count_timeseries, pace_grouped)


def readGlobalPace(dirName):
	paceFileName = os.path.join(dirName, "global_features.csv")
	
	#Read the pace file
	r = csv.reader(open(paceFileName, "r"))
	colIds = getHeaderIds(r.next())
	
	pace_timeseries = {}

		
	
	for line in r:
		#Extract info
		#First 3 columns
		date = line[colIds["Date"]]
		hour = int(line[colIds["Hour"]])
		weekday = line[colIds["Weekday"]]
		#Last 16 columns
		pace = float(line[colIds["Pace"]])
		

		#Save vector in the timeseries and the group
		pace_timeseries[(date, hour, weekday)] = pace

	return pace_timeseries


def trace(m):
	s = 0.0
	for i in range(len(m)):
		s += m[i,i]
	return s


#in the odds-ratio, 0 is the numerator, 1 is the demonimator
def gaussian_kl_divergence(mu0, sig0, mu1, sig1):
	dim = len(mu1)
	
	#Invert the matrix once upfront, so we don't have to do it twice later
	try:
		inv_sig1 = inv(sig1)
	
	
	
		v = .5 * (trace(inv_sig1*sig0) + \
			transpose(mu1 - mu0)*inv_sig1*(mu1-mu0) - \
			dim - \
			log(det(sig0) / det(sig1)))[0,0]
	
	except:
		#print sig1
		raise MyException()
	
	return v

def gaussian_likelihood(mu, sig, obs):
	denom = math.sqrt((2*math.pi)**len(mu) * det(sig))
	pwr = -.5 * transpose(obs - mu) * inv(sig) * (obs - mu)
	return math.exp(pwr) / denom

def gaussian_loglik(mu, sig, obs):
	logdenom = -.5*len(mu) * math.log(2*math.pi) - .5*math.log(det(sig))
	pwr = -.5 * transpose(obs - mu) * inv(sig) * (obs - mu)
	return (logdenom + pwr)[0,0]

def gaussian_loglik_scaled(mu, sig, obs):
	if(len(mu)==0):
		return 0
		
	logdenom = -.5*len(mu) * math.log(2*math.pi)
	pwr = -.5 * transpose(obs - mu) * inv(sig) * (obs - mu)
	return (logdenom + pwr)[0,0]
	

#m[[1,2],:][:,[1,2]]
def extract_valid_params(mu, sig, obs):
	valid_ids = []
	for i in range(len(obs)):
		if(not obs[i]==0):
			valid_ids.append(i)
	
	if(len(valid_ids)==len(sig)):
		return (mu, sig, obs)
	
	
	mu_subset = mu[valid_ids]
	sig_subset = sig[valid_ids,:][:,valid_ids]
	obs_subset = obs[valid_ids]	
	
	return (mu_subset, sig_subset, obs_subset)	

def generateTimeSeries():
	numpy.set_printoptions(linewidth=1000, precision=4)
	logMsg("Reading files...")
	(pace_timeseries, var_timeseries, count_timeseries, pace_grouped) = readPaceData("4year_features")
	
		

	logMsg("Estimating distribution parameters...")	
	mvGaussFull = {}
	mvGaussDiag = {}
	
	for key in pace_grouped:
		samp = pace_grouped[key]
		mu = matrix(mean(samp, axis=0))
		sig_full = estimate_cov_param(samp)
		sig_diag = estimate_cov_independent(samp)
		
		mvGaussFull[key] = MVGaussian(mu, sig_full)
		mvGaussDiag[key] = MVGaussian(mu, sig_diag)
		return
		
		
	logMsg("Computing KL Divergence...")	
	kl_timeseries = {}
	ind_timeseries = {}
		
	it = 0
	for (date, hour, weekday) in sorted(pace_timeseries):
		logPerc(it, len(pace_timeseries), 1)
		it+=1
		
		mu0 = pace_timeseries[(date, hour, weekday)]

		#Variance of mean observation = variance / n
		std_err_of_mean = var_timeseries[(date, hour, weekday)] / count_timeseries[(date, hour, weekday)]	
		
		
		sig0 = diag(transpose(std_err_of_mean).tolist()[0])/ 209
		
		#samp = pace_grouped[(weekday, hour)]
		#mu1 = matrix(mean(samp, axis=0))
		#sig1 = estimate_cov_full(samp)
		
		#(mu1_sub, sig1_sub, obs_sub) = extract_valid_params(mu1, sig1, mu0)

		
		#sig2 = estimate_cov_independent(samp)		
		#(mu1_sub, sig2_sub, obs_sub) = extract_valid_params(mu1, sig2, mu0)
		

		fullDistrib = mvGaussFull[(weekday, hour)]		
		indDistrib = mvGaussDiag[(weekday, hour)]
		
		"""
		print ("*********************************************************************")
		print mu0		
		print sig0
		print ("*********************************************************************")
		print mu1	
		print sig1
		"""
		try:
			#kl_timeseries[(date, hour,weekday)] = gaussian_kl_divergence(mu0, sig0, mu1, sig1)
			#kl_timeseries[(date, hour, weekday)] = gaussian_loglik(mu1, sig1, mu0) - gaussian_loglik(mu1, sig1, mu1)
			#kl_timeseries[(date, hour, weekday)] = gaussian_kl_divergence(mu0, sig0, mu1, sig1) - gaussian_loglik(mu1, sig1, mu1)
			kl_timeseries[(date, hour, weekday)] = fullDistrib.gaussian_loglik_scaled(mu0)
			ind_timeseries[(date, hour, weekday)] = indDistrib.gaussian_loglik_scaled(mu0)
		except (MyException, ZeroDivisionError):
			kl_timeseries[(date, hour,weekday)] = 0
			ind_timeseries[(date, hour,weekday)] = 0
	
	global_pace_timeseries = readGlobalPace("4year_features")
	
	
	
	w = csv.writer(open("results/kl_over_time.csv", "w"))
	w.writerow(['date','hour','weekday','kl', 'ind','global_pace'])
	for (date, hour, weekday) in sorted(pace_timeseries):
		kl = kl_timeseries[(date,hour,weekday)]
		ind = ind_timeseries[(date,hour,weekday)]
		gl_pace = global_pace_timeseries[(date, hour, weekday)]
		w.writerow([date, hour, weekday, kl, ind, gl_pace])



	
	
	
	
	
	

generateTimeSeries()