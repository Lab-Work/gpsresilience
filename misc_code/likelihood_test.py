# -*- coding: utf-8 -*-
"""
Created on Wed May 21 17:37:25 2014

@author: brian
"""
import numpy
from numpy import matrix, transpose, mean
import os, csv
from collections import defaultdict
import pickle
import sys

from cov_matrix import *
from eventDetection import *
from tools import *


USE_EXPECTED_LNL = False





#Reads time-series pace data from a file, and sorts it into a convenient format.
#Params:
	#dirName - the directory which contains time-series features (produced by extractGridFeatures.py)
	#returns - (pace_timeseries, var_timeseries, count_timeseries, pace_grouped).  Breakdown:
		#pace_timeseries - a dictionary which maps (date, hour, weekday) to the corresponding average pace vector (average pace of each trip type)
		#var_timeseries - a dictionary which maps (date, hour, weekday) to the corresponding pace variance vector (variance of paces of each trip type)
		#count_timeseries - a dictionary which maps (date, hour, weekday) to the corresponding count vector (number of occurrences of each trip type)
		#pace_grouped - a dictionary which maps (weekday, hour) to the list of corresponding pace vectors
		#		for example, ("Wednesday", 5) maps to the list of all pace vectors that occured on a Wednesday at 5am.
def readPaceData(dirName):
	logMsg("Reading files from " + dirName + " ...")
	#Create filenames
	paceFileName = os.path.join(dirName, "pace_features.csv")
	paceVarFileName = os.path.join(dirName, "pace_var_features.csv")	
	countFileName = os.path.join(dirName, "count_features.csv")
	
	#Initialize dictionaries	
	pace_timeseries = {}
	pace_grouped = defaultdict(list)
	var_timeseries = {}
	count_timeseries = {}	
	
	#Read the pace file
	r = csv.reader(open(paceFileName, "r"))
	colIds = getHeaderIds(r.next())
	
	#Read the file line by line
	for line in r:
		#Extract info
		#First 3 columns
		date = line[colIds["Date"]]
		hour = int(line[colIds["Hour"]])
		weekday = line[colIds["Weekday"]]
		
		#The rest of the columns contain paces
		paces = map(float, line[3:])
		
		#Convert to numpy column vector
		v = transpose(matrix(paces))
		#Save vector in the timeseries
		pace_timeseries[(date, hour, weekday)] = v
		
		#If there is no missing data, save the vector into the group
		if(allNonzero(v)):
			pace_grouped[(weekday, hour)].append(v)

	
	
	#Read pace variance file
	r = csv.reader(open(paceVarFileName, "r"))
	colIds = getHeaderIds(r.next())

	#Red the file line by line
	for line in r:
		#Extract info
		#First 3 columns
		date = line[colIds["Date"]]
		hour = int(line[colIds["Hour"]])
		weekday = line[colIds["Weekday"]]
		
		#the rest of the columns contain pace variances
		paces = map(float, line[3:])
		
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
		
		#Last The rest of the columns contain trip counts
		counts = map(float, line[3:])
		
		#Convert to numpy column vector
		v = transpose(matrix(counts))
		#Save vector in the timeseries
		count_timeseries[(date, hour, weekday)] = v
	
	#return time series and grouped data
	return (pace_timeseries, var_timeseries, count_timeseries, pace_grouped)


#Reads the time-series global pace from a file and sorts it into a convenient format
#Params:
	#dirName - the directory which contains time-series features (produced by extractGridFeatures.py)
	#returns - a dictionary which maps (date, hour, weekday) to the average pace of all taxis in that timeslice
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




#Fits distributions to each group of pace vectors
#For example, the distribution of all pace vectors on Mondays at 6pm.
#The distributions are all Multivariate Gaussian, but the covariance matrices are computed in 3 ways:
	#1) Full sample covariance
	#2) Diagonal sample covariance - assumes that dimensions of the pace vectors are uncorrelated (all non-diagonal entries of the covariance matrix are 0)
	#3) Parameterized sample covariance - assumes that the covariance matrix is a function of a small number of parameters.  This parameterization is discussed further in cov_matrix.py
#Params:
	#pace_grouped - a dictionary which maps (weekday, hour) to a list of pace vectors.
	#		I.E. the output from readPaceData
	#returns - (mvGaussFull, mvGaussDiag, mvGaussParam).  3 Dictionaries which map (weekday, hour) to the respective distributions discussed above
def generateDistributions(pace_grouped):
	logMsg("Estimating distribution parameters...")
	#Initialize dictionaries
	mvGaussFull = {}
	mvGaussDiag = {}
	mvGaussParam = {}	
	
	i = 0	
	for key in pace_grouped:
		#Retrieve group of pace vectors
		samp = pace_grouped[key]
		
		#Compute mean pace vector
		mu = matrix(mean(samp, axis=0))
		
		i += 1
		logMsg("Fitting distribution " + str(i) + "/" + str(len(pace_grouped)))
		logMsg("--full")
		#Fit the full sample covariance
		sig_full = estimate_cov_full(samp)
		mvGaussFull[key] = MVGaussian(mu, sig_full)		
		
		logMsg("--independent")
		#Fit the diagonal sample covariance
		sig_diag = estimate_cov_independent(samp)
		mvGaussDiag[key] = MVGaussian(mu, sig_diag)
		
		logMsg("--parameterized")
		#Fit the parameterized sample covariance
		sig_param = estimate_cov_param(samp)
		mvGaussParam[key] = MVGaussian(mu, sig_param)
	
	return (mvGaussFull, mvGaussDiag, mvGaussParam)

#Computes shrinkage estimators of the covariance matrix - weighted compromises between the full matrix and the parameterized matrix
#Params:
	#mvGaussFull - the dictionary which contains full sample covariance matrices.  One of the outputs from generateDistributions()
	#mvGaussParam - the dictionary which contains parameterized sample covariance matrices. Another output from generateDistributions()
	#shrinkageCoefs - a list of shrinkage coefficients (values between 0 and 1)
	#		Note that higher values place more weight on the full covariance and lower values place more weight on the parameterized covariance
	#returns - a dictionary which maps (weekday, hour, coef) to the corresponding MVGaussian distribution
def generateShrinkageDistributions(mvGaussFull, mvGaussParam, shrinkageCoefs):
	mvGaussShrink = {}
	#Iterate through all distributions
	for (weekday, hour) in mvGaussFull:
		for coef in shrinkageCoefs:
			#Generate the distribution, whose covariance matrix is a weighted average of the full and parameterized distributions
			mvg = MVGaussian.mix(mvGaussFull[(weekday,hour)], mvGaussParam[(weekday,hour)], coef)
			#save in the dictionary
			mvGaussShrink[(weekday, hour, coef)] = mvg
	#return the dictionary
	return mvGaussShrink
		

#Reads time series pace data from a CSV file, and fits 3 types of distributions to it
#These 3 distributions are saved as dictionaries in a .pickle file
#The purpose of this is to save intermediate results, so they do not have to be recomputed
#Params:
	#inDir - the directory which contains the time-series feature files (CSV format)
	#outFile - the .pickle file that the distributions will be saved in
def saveDistributions(inDir, outFile):
	numpy.set_printoptions(linewidth=1000, precision=4)
	

	(pace_timeseries, var_timeseries, count_timeseries, pace_grouped) = readPaceData(inDir)
	(mvGaussFull, mvGaussDiag, mvGaussParam) = generateDistributions(pace_grouped)
	
	logMsg("Saving...")
	with open(outFile, 'wb') as f:
		pickle.dump((mvGaussFull, mvGaussDiag, mvGaussParam), f)
	
	logMsg("Done.")


#Generates time-series log-likelihood values.
#These describe how likely or unlikely the state of the city is, given the distribution of "similar" days (same hour and day of week)
#Params:
	#inDir - the directory which contains the time-series feature files (CSV format)
	#distributions - 3 dictionaries, which map (weekday, hour) to 3 different types of distributions
	#		 Can be created by generateDistributions() or read from the .pickle file
	#returns - no return value, but saves files into results/...
def generateTimeSeries(inDir, distributions):
	numpy.set_printoptions(linewidth=1000, precision=4)
	
	#unpack the distributions
	(mvGaussFull, mvGaussDiag, mvGaussParam) = distributions
	
	
	
	logMsg("Shrinking...")
	#Create shrinkage distributions
	shrinkageCoefs = [float(i) / 10 for i in range(11)]
	mvGaussShrink = generateShrinkageDistributions(mvGaussFull, mvGaussParam, shrinkageCoefs)	
	
	#Read the time-series data from the file
	logMsg("Reading files...")
	(pace_timeseries, var_timeseries, count_timeseries, pace_grouped) = readPaceData(inDir)
	
		

	
		
	logMsg("Computing Likelihoods...")	
	full_timeseries = {} #Lnl timeseries from distributions with full covariance matrix
	ind_timeseries = {}  #Lnl timeseries from distributions with diagonal (independent) covariance matrix
	param_timeseries = {} #Lnl timeseries from distribution with parameterized covariance matrix
	
	shrinkage_timeseries = {} #Lnl timeseries from compromise between full and parameterized (for various shrinkage coefficients)
	it = 0
	#Iterate through the time-series in chronological order
	for (date, hour, weekday) in sorted(pace_timeseries):
		logPerc(it, len(pace_timeseries), 1)
		it+=1
		
		
		mu0 = pace_timeseries[(date, hour, weekday)] #The mean pace vector at a given point in time
		
		#There is some uncertainty of this mean, due to variations of individual trips in this hour
		#Squared standard error of the mean = variance / n
		squared_std_err_of_mean = var_timeseries[(date, hour, weekday)] / count_timeseries[(date, hour, weekday)]
		#Convert independent variance measurements to a diagonal covariance matrix
		sig0 = diag(transpose(squared_std_err_of_mean).tolist()[0])
		

		
		#Grab the corresponding distributions for the current time of day/week
		fullDistrib = mvGaussFull[(weekday, hour)]		
		indDistrib = mvGaussDiag[(weekday, hour)]
		paramDistrib = mvGaussParam[(weekday, hour)]
		
		"""
		print ("*********************************************************************")
		print mu0		
		print sig0
		print ("*********************************************************************")
		print mu1	
		print sig1
		"""
		try:

			
			#Compute the expected likelihoods (taking into account the uncertainty of the current mean pace vector)
			if(USE_EXPECTED_LNL):
				full_timeseries[(date, hour, weekday)] = fullDistrib.expected_loglik_scaled(mu0, sig0)
				ind_timeseries[(date, hour, weekday)] = indDistrib.expected_loglik_scaled(mu0, sig0)
				param_timeseries[(date, hour, weekday)] = paramDistrib.expected_loglik_scaled(mu0, sig0)
			else:
				full_timeseries[(date, hour, weekday)] = fullDistrib.gaussian_loglik_scaled(mu0)
				ind_timeseries[(date, hour, weekday)] = indDistrib.gaussian_loglik_scaled(mu0)
				param_timeseries[(date, hour, weekday)] = paramDistrib.gaussian_loglik_scaled(mu0)
			
			#Also perform the likelihood test on the shrinkage estimates
			#there are many different shrinkage coefficients
			for coef in shrinkageCoefs:
				shrinkDistrib = mvGaussShrink[(weekday, hour, coef)]
				if(USE_EXPECTED_LNL):
					shrinkage_timeseries[(date, hour, weekday, coef)] = shrinkDistrib.expected_loglik_scaled(mu0, sig0)
				else:
					shrinkage_timeseries[(date, hour, weekday, coef)] = shrinkDistrib.gaussian_loglik_scaled(mu0)
				
		except (ZeroDivisionError):
			full_timeseries[(date, hour,weekday)] = 0
			ind_timeseries[(date, hour,weekday)] = 0
			param_timeseries[(date, hour, weekday)] = 0
	
	
	#Also read the global pace file
	global_pace_timeseries = readGlobalPace("4year_features")
	(expected_pace_timeseries, sd_pace_timeseries) = getExpectedPace(global_pace_timeseries)
	
	if(USE_EXPECTED_LNL):
		lnl_cov_file = "results/expected_lnl_over_time_cov.csv"
		lnl_shrink_file = "results/expected_lnl_over_time_shrink.csv"
	else:
		lnl_cov_file = "results/lnl_over_time_cov.csv"
		lnl_shrink_file = "results/lnl_over_time_shrink.csv"
	
	#output results to a file
	w = csv.writer(open(lnl_cov_file, "w"))
	w.writerow(['date','hour','weekday','full_lnl', 'ind_lnl', "param_lnl" ,'global_pace', 'expected_pace', 'sd_pace'])
	for (date, hour, weekday) in sorted(pace_timeseries):
		full = full_timeseries[(date,hour,weekday)]
		ind = ind_timeseries[(date,hour,weekday)]
		param = param_timeseries[(date, hour, weekday)]
		gl_pace = global_pace_timeseries[(date, hour, weekday)]
		exp_pace = expected_pace_timeseries[(date, hour, weekday)]
		sd_pace = sd_pace_timeseries[(date, hour, weekday)]
		w.writerow([date, hour, weekday, full, ind, param, gl_pace, exp_pace, sd_pace])



	#output shrinkage results to a second file
	w = csv.writer(open(lnl_shrink_file, "w"))
	shrink_header = ["shrink_" + str(int(v*10)) for v in shrinkageCoefs]	
	
	w.writerow(['date','hour','weekday'] + shrink_header)
	for (date, hour, weekday) in sorted(pace_timeseries):
		shrink_lnl = []
		for coef in shrinkageCoefs:
			shrink_lnl.append(shrinkage_timeseries[(date,hour,weekday,coef)])
		w.writerow([date, hour, weekday] + shrink_lnl)
	
	
	
#Generates time-series log-likelihood values
#Similar to generateTimeSeries(), but LEAVES OUT the current observation when computing the probability
#These describe how likely or unlikely the state of the city is, given the distribution of "similar" days (same hour and day of week)
#Params:
	#inDir - the directory which contains the time-series feature files (CSV format)
	#returns - no return value, but saves files into results/...
def generateTimeSeriesLeave1(inDir):
	numpy.set_printoptions(linewidth=1000, precision=4)
	
	#Read the time-series data from the file
	logMsg("Reading files...")
	(pace_timeseries, var_timeseries, count_timeseries, pace_grouped) = readPaceData(inDir)
	
	
	shrinkageCoefs = [float(i) / 10 for i in range(11)]
		

	
		
	logMsg("Computing Likelihoods...")	
	full_timeseries = {} #Lnl timeseries from distributions with full covariance matrix
	ind_timeseries = {}  #Lnl timeseries from distributions with diagonal (independent) covariance matrix
	param_timeseries = {} #Lnl timeseries from distribution with parameterized covariance matrix
	
	
	
	#We will also be writing a file which contains the standardized pace vectors (zscores)
	zscore_writer = csv.writer(open("results/std_pace_vector.csv", "w"))
	zscore_writer.writerow(['Date','Hour','Weekday','E-E','E-U','E-M','E-L','U-E','U-U','U-M','U-L','M-E','M-U','M-M','M-L','L-E','L-U','L-M','L-L'])
	
	
	
	
	shrinkage_timeseries = {} #Lnl timeseries from compromise between full and parameterized (for various shrinkage coefficients)
	it = 0
	#Iterate through the time-series in chronological order
	for (date, hour, weekday) in sorted(pace_timeseries):
		logPerc(it, len(pace_timeseries), 1)
		it+=1
		
		
		mu0 = pace_timeseries[(date, hour, weekday)] #The mean pace vector at a given point in time
		
		#There is some uncertainty of this mean, due to variations of individual trips in this hour
		#Squared standard error of the mean = variance / n
		squared_std_err_of_mean = var_timeseries[(date, hour, weekday)] / count_timeseries[(date, hour, weekday)]
		#Convert independent variance measurements to a diagonal covariance matrix
		sig0 = diag(transpose(squared_std_err_of_mean).tolist()[0])
		

		
		
		
		samp = pace_grouped[(weekday, hour)]
		leave1_samp = allBut(samp, mu0) #Leave the current value out of the sample
		
		#Compute mean pace vector
		mu = matrix(mean(leave1_samp, axis=0))


		#Fit the full sample covariance
		sig_full = estimate_cov_full(leave1_samp)
		fullDistrib = MVGaussian(mu, sig_full)		
		
		#Fit the diagonal sample covariance
		sig_diag = estimate_cov_independent(leave1_samp)
		indDistrib = MVGaussian(mu, sig_diag)
		


		std_pace_vect = fullDistrib.standardize_vector(mu0)
		zscores = [float(std_pace_vect[i]) for i in range(len(std_pace_vect))]
		zscore_writer.writerow([date, hour, weekday] + zscores)
		
		#Grab the corresponding distributions for the current time of day/week
		#fullDistrib = mvGaussFull[(weekday, hour)]		
		#indDistrib = mvGaussDiag[(weekday, hour)]
		#paramDistrib = mvGaussParam[(weekday, hour)]
		
		"""
		print ("*********************************************************************")
		print mu0		
		print sig0
		print ("*********************************************************************")
		print mu1	
		print sig1
		"""
		try:

			
			#Compute the expected likelihoods (taking into account the uncertainty of the current mean pace vector)
			if(USE_EXPECTED_LNL):
				full_timeseries[(date, hour, weekday)] = fullDistrib.expected_loglik_scaled(mu0, sig0)
				ind_timeseries[(date, hour, weekday)] = indDistrib.expected_loglik_scaled(mu0, sig0)
				param_timeseries[(date, hour, weekday)] = 1 # Placeholder
			else:
				full_timeseries[(date, hour, weekday)] = fullDistrib.gaussian_loglik_scaled(mu0)
				ind_timeseries[(date, hour, weekday)] = indDistrib.gaussian_loglik_scaled(mu0)
				param_timeseries[(date, hour, weekday)] = 1 # Placeholder
			
			#Also perform the likelihood test on the shrinkage estimates
			#there are many different shrinkage coefficients
			for coef in shrinkageCoefs:
				#shrinkDistrib = MVGaussian.mix(fullDistrib, indDistrib, coef)
				if(USE_EXPECTED_LNL):
					shrinkage_timeseries[(date, hour, weekday, coef)] = 1#shrinkDistrib.expected_loglik_scaled(mu0, sig0)
				else:
					shrinkage_timeseries[(date, hour, weekday, coef)] = 1#shrinkDistrib.gaussian_loglik_scaled(mu0)
				
		except (ZeroDivisionError):
			full_timeseries[(date, hour,weekday)] = 1
			ind_timeseries[(date, hour,weekday)] = 1
			param_timeseries[(date, hour, weekday)] = 1
	
	
	#Also read the global pace file
	global_pace_timeseries = readGlobalPace("4year_features")
	(expected_pace_timeseries, sd_pace_timeseries) = getExpectedPace(global_pace_timeseries)
	
	if(USE_EXPECTED_LNL):
		lnl_cov_file = "results/expected_lnl_over_time_leave1.csv"
		lnl_shrink_file = "results/expected_lnl_over_time_shrink_leave1.csv"
	else:
		lnl_cov_file = "results/lnl_over_time_leave1.csv"
		lnl_shrink_file = "results/lnl_over_time_shrink_leave1.csv"
	
	#output results to a file
	w = csv.writer(open(lnl_cov_file, "w"))
	w.writerow(['date','hour','weekday','full_lnl', 'ind_lnl', "param_lnl" ,'global_pace', 'expected_pace', 'sd_pace'])
	for (date, hour, weekday) in sorted(pace_timeseries):
		full = full_timeseries[(date,hour,weekday)]
		ind = ind_timeseries[(date,hour,weekday)]
		param = param_timeseries[(date, hour, weekday)]
		gl_pace = global_pace_timeseries[(date, hour, weekday)]
		exp_pace = expected_pace_timeseries[(date, hour, weekday)]
		sd_pace = sd_pace_timeseries[(date, hour, weekday)]
		w.writerow([date, hour, weekday, full, ind, param, gl_pace, exp_pace, sd_pace])



	#output shrinkage results to a second file
	w = csv.writer(open(lnl_shrink_file, "w"))
	shrink_header = ["shrink_" + str(int(v*10)) for v in shrinkageCoefs]	
	
	w.writerow(['date','hour','weekday'] + shrink_header)
	for (date, hour, weekday) in sorted(pace_timeseries):
		shrink_lnl = []
		for coef in shrinkageCoefs:
			shrink_lnl.append(shrinkage_timeseries[(date,hour,weekday,coef)])
		w.writerow([date, hour, weekday] + shrink_lnl)




if(__name__=="__main__"):
	#saveDistributions("4year_features", "results/covariance_matrices.pickle")
	print sys.argv
	
	if(len(sys.argv) > 1):
		if(sys.argv[1]=='expected'):
			logMsg("Using expected likelihood")
			USE_EXPECTED_LNL = True
	
	#with open("results/covariance_tmp.pickle", "rb") as f:
	#	logMsg("Loading distributions from file...")
	#	distributions = pickle.load(f)
	#	generateTimeSeries("4year_features", distributions)
	
	generateTimeSeriesLeave1("4year_features")