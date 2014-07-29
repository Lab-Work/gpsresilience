# -*- coding: utf-8 -*-
"""
Created on Wed May 21 17:37:25 2014

@author: brian
"""
import numpy
from numpy import matrix, transpose, mean, diag
import os, csv
from collections import defaultdict
import pickle
import sys
from multiprocessing import Process, Queue
from gaussian_kernel import *


from cov_matrix import *
from eventDetection import *
from tools import *


NUM_CPUS = 8
COMPUTE_KERNEL = False


#A worker process which computes probabilities for a slice of dates
class LikelihoodComputationProcess(Process):
	def __init__(self, pace_timeseries, pace_grouped, groupedStats, start_id, end_id):
		super(LikelihoodComputationProcess, self).__init__()
		self.pace_grouped = pace_grouped
		self.pace_timeseries = pace_timeseries
		self.groupedStats = groupedStats
		self.start_id = start_id
		self.end_id = end_id
		
		self.prob_output_queue = Queue()
		self.zscore_output_queue = Queue()
	
	def say(self, msg):
		logMsg(str(self.start_id) + "-" + str(self.end_id) + " " + msg)
		
	def run(self):
		
		
		(s_x, s_xxt, count) = self.groupedStats
		
		
		
		if(COMPUTE_KERNEL):
			kernels = {}
			for key in self.pace_grouped:
				kernels[key] = MVGaussianKernel(self.pace_grouped[key])
		
		full_timeseries = {}
		ind_timeseries = {}
		kernel_timeseries = {}
		
		#Iterate through the time-series in chronological order
		sorted_dates = sorted(self.pace_timeseries)
		#But only consider the slice assigned to this iprocess		
		for i in range(self.start_id, self.end_id):
			(date, hour, weekday) = sorted_dates[i] 

			logPerc(i - self.start_id, self.end_id - self.start_id, 2)
			
			
			mu0 = self.pace_timeseries[(date, hour, weekday)] #The mean pace vector at a given point in time
						
			
			
			#samp = pace_grouped[(weekday, hour)]
			#leave1_samp = allBut(samp, mu0) #Leave the current value out of the sample
			#print(len(leave1_samp))
			
			
			#Compute mean pace vector
			#mutest = matrix(mean(leave1_samp, axis=0))
	
			#Use the grouped stats and the current vector (mu0) to compute the leave-1-out mean and covariance
			(mu, sig_full) = computeLeave1Stats(s_x, s_xxt, count, mu0, weekday, hour)

			
			#Extract diagonal components of the covariance matrix (independence assumption)
			sig_diag = diag(diag(sig_full))
			


			fullDistrib = MVGaussian(mu, sig_full)
			indDistrib = MVGaussian(mu, sig_diag)

			std_pace_vect = fullDistrib.standardize_vector(mu0)
			zscores = [float(std_pace_vect[i]) for i in range(len(std_pace_vect))]
			self.zscore_output_queue.put([date, hour, weekday] + zscores)
			
			#Grab the corresponding distributions for the current time of day/week
			#fullDistrib = mvGaussFull[(weekday, hour)]		
			#indDistrib = mvGaussDiag[(weekday, hour)]
			#paramDistrib = mvGaussParam[(weekday, hour)]
			

			try:
				full_timeseries[(date, hour, weekday)] = fullDistrib.gaussian_loglik_scaled(mu0)
				ind_timeseries[(date, hour, weekday)] = indDistrib.gaussian_loglik_scaled(mu0)
									
			except (ZeroDivisionError):
				full_timeseries[(date, hour,weekday)] = 1
				ind_timeseries[(date, hour,weekday)] = 1
			
			if(COMPUTE_KERNEL):
				kernel = kernels[weekday, hour]
				kernel_timeseries[date, hour, weekday] = kernel.loglik_scaled(mu0)
			else:
				kernel_timeseries[date, hour, weekday] = 1
	
		self.say(" finished computing.")
		self.prob_output_queue.put(full_timeseries)
		self.say(" put 1.")
		self.prob_output_queue.put(ind_timeseries)
		self.say(" put 2.")
		self.prob_output_queue.put(kernel_timeseries)
		self.say(" is complete.")
	


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



def computeGroupedStats(pace_timeseries):
	count = {}	#count of all vectors (0th moneht)
	s_x = {} 	#sum of all vectors (1st moment)
	s_xxt = {}	#sum of all outer products x * transpose(x) (2nd moment)
	
	for (date, hour, weekday) in pace_timeseries:
		x = pace_timeseries[date, hour, weekday]
		if((weekday,hour) not in s_x):
			s_x[weekday, hour] = matrix(zeros((len(x),1)))
			s_xxt[weekday, hour] = matrix(zeros((len(x),len(x))))
			count[weekday, hour] = 0.0
			
		if(allNonzero(x)):
			s_x[weekday, hour] += x
			s_xxt[weekday, hour] += x * transpose(x)
			count[weekday, hour] += 1

			
	return (s_x, s_xxt, count)


def computeLeave1Stats(s_x, s_xxt, count, x, weekday, hour):
	if(allNonzero(x)):
		new_s_x = s_x[weekday, hour] - x
		new_s_xxt = s_xxt[weekday, hour] - x * transpose(x)
		new_count = count[weekday, hour] - 1
	else:
		new_s_x = s_x[weekday, hour]
		new_s_xxt = s_xxt[weekday, hour]
		new_count = count[weekday, hour]
	
	mu = new_s_x / new_count
	
	#var(x) = E[x**2] - E[x]**2.  Multiply by n/(n-1) for unbiased covariance correction
	sigma = (new_s_xxt / new_count - mu * transpose(mu)) * (new_count / (new_count - 1))
	return (mu, sigma)

def scale_kern_timeseries(kern_timeseries):
	max_val = defaultdict(lambda : float('-inf'))
	for (date, hour, weekday) in kern_timeseries:
		p = kern_timeseries[date, hour, weekday]
		if(p < 0):
			max_val[weekday, hour] = max(max_val[weekday, hour], kern_timeseries[date, hour, weekday])

	for (date, hour, weekday) in kern_timeseries:
		kern_timeseries[date, hour, weekday] -= max_val[weekday, hour]
	
	



	
#Generates time-series log-likelihood values
#Similar to generateTimeSeries(), but LEAVES OUT the current observation when computing the probability
#These describe how likely or unlikely the state of the city is, given the distribution of "similar"
# days (same hour and day of week) but not today.
#Params:
	#inDir - the directory which contains the time-series feature files (CSV format)
	#returns - no return value, but saves files into results/...
def generateTimeSeriesLeave1(inDir):
	numpy.set_printoptions(linewidth=1000, precision=4)
	
	#Read the time-series data from the file
	logMsg("Reading files...")
	(pace_timeseries, var_timeseries, count_timeseries, pace_grouped) = readPaceData(inDir)
	
	
		

	logMsg("Computing grouped stats...")
	groupedStats = computeGroupedStats(pace_timeseries)
	
		
	logMsg("Starting Processes...")
	
	
	full_timeseries = {} #Lnl timeseries from distributions with full covariance matrix
	ind_timeseries = {}  #Lnl timeseries from distributions with diagonal (independent) covariance matrix
	kern_timeseries = {}
	
	workers = []
	num_dates = len(pace_timeseries)
	logMsg("Splitting " + str(num_dates) + " dates into " + str(NUM_CPUS) + " pieces.")
	for (lo, hi) in splitRange(num_dates, NUM_CPUS):
		print (lo, hi)
		worker = LikelihoodComputationProcess(pace_timeseries, pace_grouped, groupedStats, lo, hi)
		worker.start()		
		#worker.run()		
		workers.append(worker)


	#We will also be writing a file which contains the standardized pace vectors (zscores)
	zscore_writer = csv.writer(open("results/std_pace_vector.csv", "w"))
	zscore_writer.writerow(['Date','Hour','Weekday','E-E','E-U','E-M','E-L','U-E','U-U','U-M','U-L','M-E','M-U','M-M','M-L','L-E','L-U','L-M','L-L'])

	
	for worker in workers:
		logMsg("Joining " + str((worker.start_id, worker.end_id)) + " ...")
		
		part_full_timeseries = worker.prob_output_queue.get()
		worker.say("got 1")
		part_ind_timeseries = worker.prob_output_queue.get()
		worker.say("got 2")
		part_kern_timeseries = worker.prob_output_queue.get()
		worker.say("got 3")

		full_timeseries.update(part_full_timeseries)
		ind_timeseries.update(part_ind_timeseries)
		kern_timeseries.update(part_kern_timeseries)
		
		while(worker.zscore_output_queue.qsize() >0):
			zscore_writer.writerow(worker.zscore_output_queue.get())
		
		logMsg("Got stuff from the queue.")
		worker.join()
		logMsg("Joined.")
	
	scale_kern_timeseries(kern_timeseries)
		
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
	w.writerow(['date','hour','weekday','full_lnl', 'ind_lnl', 'kern_lnl' ,'global_pace', 'expected_pace', 'sd_pace'])
	for (date, hour, weekday) in sorted(pace_timeseries):
		full = full_timeseries[(date,hour,weekday)]
		ind = ind_timeseries[(date,hour,weekday)]
		kern = kern_timeseries[date, hour,weekday]
		gl_pace = global_pace_timeseries[(date, hour, weekday)]
		exp_pace = expected_pace_timeseries[(date, hour, weekday)]
		sd_pace = sd_pace_timeseries[(date, hour, weekday)]
		w.writerow([date, hour, weekday, full, ind, kern, gl_pace, exp_pace, sd_pace])




if(__name__=="__main__"):
	#saveDistributions("4year_features", "results/covariance_matrices.pickle")
	print (sys.argv)
	
	if(len(sys.argv) > 1):
		if(sys.argv[1]=='expected'):
			logMsg("Using expected likelihood")
			USE_EXPECTED_LNL = True
	
	#with open("results/covariance_tmp.pickle", "rb") as f:
	#	logMsg("Loading distributions from file...")
	#	distributions = pickle.load(f)
	#	generateTimeSeries("4year_features", distributions)
	
	generateTimeSeriesLeave1("4year_features")