# -*- coding: utf-8 -*-
"""
Performs the likelihood computation on mean pace vectors.  It should be run AFTER extractRegionFeaturesParallel.py

Created on Wed May 21 17:37:25 2014

@author: Brian Donovan (briandonovan100@gmail.com)
"""
import numpy
from numpy import matrix, transpose, diag
import os, csv
from collections import defaultdict
from multiprocessing import Pool
from gaussian_kernel import *
import traceback

from mvGaussian import *
from eventDetection import *
from tools import *


NUM_PROCESSORS = 8
IN_DIR = "4year_features"	#Location of features folder (output of extractRegionFeaturesParallel)
OUT_PROB_FILE = "results/lnl_over_time_leave1.csv"	#Where to output probability file
OUT_ZSCORE_FILE = "results/std_pace_vector.csv"		#Where to ouput zscores file

#Use Kernel Density Estimate, in addition to Gaussian Distributions?
#Note : This is much slower
COMPUTE_KERNEL = True



#Produces the probability timeseries for a slice of the data
#Many slices can be run in parallel
#Arguments: Takes a tuple for ease of use with Pool.map().  Breakdown:
	#pace_timeseries - a dictionary which maps (date, hour, weekday) -> mean pace vector for that time slice
	#pace_grouped - a dictionary which maps (weekday, hour) -> list of mean pace vectors for that point in the periodic pattern
	#groupedStats - a dictionary which maps (weekday, hour) -> the 0th, 1st, and 2nd moments of the data. see computeGroupedStats()
	#start_id - the start of the slice to be computed by this thread
	#end_id - the end of the slice to be computed by this thread
def generateTimeSlice((pace_timeseries, pace_grouped, groupedStats, start_id, end_id)):
	try:
		(s_x, s_xxt, count) = groupedStats
			
		
		
		if(COMPUTE_KERNEL):
			kernels = {}
			for key in pace_grouped:
				kernels[key] = MVGaussianKernel(pace_grouped[key])
		
		#Dictionaries which will store the output for this slice
		#These dictionaries are all keyed by (date, hour, weekday)
		full_timeseries = {}
		ind_timeseries = {}
		kernel_timeseries = {}
		zscore_timeseries = {}	
		
		#Iterate through the time-series in chronological order
		sorted_dates = sorted(pace_timeseries)
		#But only consider the slice assigned to this iprocess		
		for i in range(start_id, end_id):
			(date, hour, weekday) = sorted_dates[i] 
	
			#Progress message
			logPerc(i - start_id, end_id - start_id, 1)
			
			
			obs = pace_timeseries[(date, hour, weekday)] #The observed mean pace vector at a given point in time
						
			
			#Use the grouped stats and the current vector (obs) to compute the leave-1-out mean and covariance
			(mu, sig_full) = computeLeave1Stats(s_x, s_xxt, count, obs, weekday, hour)
	
			
			
			
			#Extract diagonal components of the covariance matrix (independence assumption)
			sig_diag = diag(diag(sig_full))
			
	
			#Create the distributions for both covariance matrices
			fullDistrib = MVGaussian(mu, sig_full)
			indDistrib = MVGaussian(mu, sig_diag)
	
			
			#Compute standardized pace vector (zscores) and save it
			std_pace_vect = fullDistrib.standardize_vector(obs)
			#print std_pace_vect
			zscores = [float(std_pace_vect[i]) for i in range(len(std_pace_vect))]		
			zscore_timeseries[date, hour, weekday] = zscores
			
	
			#Use the two gaussian distributions to compute the log-probability
			try:
				full_timeseries[(date, hour, weekday)] = fullDistrib.gaussian_loglik_scaled(obs)
				ind_timeseries[(date, hour, weekday)] = indDistrib.gaussian_loglik_scaled(obs)
									
			except (ZeroDivisionError):
				full_timeseries[(date, hour,weekday)] = 1
				ind_timeseries[(date, hour,weekday)] = 1
			
			#If desired, also compute the kernel density estimate
			if(COMPUTE_KERNEL):
				kernel = kernels[weekday, hour]
				kernel_timeseries[date, hour, weekday] = kernel.loglik_scaled(obs)
			else:
				kernel_timeseries[date, hour, weekday] = 1
	
		#Return the dictionaries computed by this process.  The caller is responsible for merging, if multiprocessing is used
	
	except Exception as e:
		traceback.print_exc()
	   	print()
		raise e
	return (full_timeseries, ind_timeseries, kernel_timeseries, zscore_timeseries)


#Iterator function - generates the tuple arguments for generateTimeslice().  Useful for multiprocessing
#Arguments:
	#pace_timeseries - a dictionary which maps (date, hour, weekday) -> mean pace vector for that time slice
	#pace_grouped - a dictionary which maps (weekday, hour) -> list of mean pace vectors for that point in the periodic pattern
	#groupedStats - a dictionary which maps (weekday, hour) -> the 0th, 1st, and 2nd moments of the data. see computeGroupedStats()
	#num_slices - how many pieces to cut pace_timeseries into?  Generally the number of available CPUs
def makeSlices(pace_timeseries, pace_grouped, groupedStats, num_slices):
	data_size = len(pace_timeseries)
	for i in range(num_slices):
		lo = int(data_size * float(i)/num_slices) #start of this slice (inclusive)
		hi = int(data_size * float(i+1)/num_slices) #end of this slice (non-inclusive)
		#note that the same pace_timeseries, pace_grouepd, and groupedStats are put into every slice
		yield (pace_timeseries, pace_grouped, groupedStats, lo, hi)

#Reduces the outputs of generateTimeSlice() if many slices are run in parallel
#Recall that generateTimeSlice() returns a tuple of dictionaries (full_timeseries, ind_timeseries, kernel_timeseries, zscore_timeseries)
#This function will merge the dictionaries across tuples.  Note that a key should appear in only one of these dictionaries, so the merging is trivial
#Arguments:
	#outputList - a list of these tuples (one for each processor)
#Returns:
	#A SINGLE tuple of the same form
def mergeOutputs(outputList):
	#Start dictionaries empty
	merged_full_timeseries = {}
	merged_ind_timeseries = {}
	merged_kernel_timeseries = {}
	merged_zscore_timeseries = {}
	
	#Iterate through all tuples in the list
	for (full_timeseries, ind_timeseries, kernel_timeseries, zscore_timeseries) in outputList:
		#Update each dictionary in the tuple
		merged_full_timeseries.update(full_timeseries)
		merged_ind_timeseries.update(ind_timeseries)
		merged_kernel_timeseries.update(ind_timeseries)
		merged_zscore_timeseries.update(zscore_timeseries)
	
	#Return the merged dictionaries
	return (merged_full_timeseries, merged_ind_timeseries, merged_kernel_timeseries, merged_zscore_timeseries)




#Reads time-series pace data from a file, and sorts it into a convenient format.
#Arguments:
	#dirName - the directory which contains time-series features (produced by extractGridFeatures.py)
#Returns:  (pace_timeseries, var_timeseries, count_timeseries, pace_grouped).  Breakdown:
	#pace_timeseries - a dictionary which maps (date, hour, weekday) to the corresponding average pace vector (average pace of each trip type)
	#var_timeseries - a dictionary which maps (date, hour, weekday) to the corresponding pace variance vector (variance of paces of each trip type)
	#count_timeseries - a dictionary which maps (date, hour, weekday) to the corresponding count vector (number of occurrences of each trip type)
	#pace_grouped - a dictionary which maps (weekday, hour) to the list of corresponding pace vectors
	#		for example, ("Wednesday", 5) maps to the list of all pace vectors that occured on a Wednesday at 5am.
def readPaceData(dirName):
	logMsg("Reading files from " + dirName + " ...")
	#Create filenames
	paceFileName = os.path.join(dirName, "pace_features.csv")

	
	#Initialize dictionaries	
	pace_timeseries = {}
	pace_grouped = defaultdict(list)

	
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

	
	#return time series and grouped data
	return (pace_timeseries, pace_grouped)


#Reads the time-series global pace from a file and sorts it into a convenient format
#Arguments:
	#dirName - the directory which contains time-series features (produced by extractGridFeatures.py)
#Returns: - a dictionary which maps (date, hour, weekday) to the average pace of all taxis in that timeslice
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



#Computes statistics for each group of mean pace vectors (the grouping is determined by the time of week)
#These statistics are the 0th (count), 1st (sum), and 2nd (sum of self-outer products) moments of the data in each of these groups
#These moments are useful because they make it easy to compute the mean or covariance matrix - THIS IS NOT DONE HERE.  IT IS DONE IN computeLeave1Stats()
#Arguments:
	#pace_grouped - a dictionary which maps (weekday, hour) --> A list of mean pace vectors that occur at that time (e.g. all mondays at 3pm)
#Returns:
	#a tuple (s_x, s_xxt, count). Breakdown:
		#s_x - a dictionary which maps (weekday, hour) --> The sum of mean pace vectors at that time (a vector)
		#s_xxt - a dictionary which maps (weekday, hour) --> The sum of outer products at that time  (a matrix)
		#count - a dictionary which maps (weekday, hour) --> The count of vectors at that time (a number)
def computeGroupedStats(pace_grouped):
	count = {}	#count of all vectors (0th moneht)
	s_x = {} 	#sum of all vectors (1st moment)
	s_xxt = {}	#sum of all outer products: x * transpose(x) (2nd moment)
	
	x = pace_grouped[arbitraryElement(pace_grouped)][0]

	
	#Iterate through all groups.  Note that key = (weekday, hour)
	for key in pace_grouped:
		#Initialize sums to zero
		s_x[key] = matrix(zeros((len(x),1)))
		s_xxt[key] = matrix(zeros((len(x),len(x))))
		
		#Get the group of mean pace vectors and store the count
		group = pace_grouped[key]
		count[key] = len(group)
		
		#Iterate through mean pace vectors, updating the appropriate counts
		for meanPaceVector in group:
			s_x[key] += meanPaceVector
			s_xxt[key] += meanPaceVector * transpose(meanPaceVector)

	#Return the thre statistics
	return (s_x, s_xxt, count)



#Compute the mean and variance of mean pace vectors that occur at the same point in time periodic pattern
#EXCEPT FOR one particular value, X.  Note that this can be done in constant time if computeGroupedStats() is already run
#Arguments:
	#s_x - output of computeGroupedStats()
	#s_xxt - output of computeGroupedStats()
	#count - output of computeGroupedStats()
	#x - a particular mean pace vector
	#weekday - the weekday on which X was observed
	#hour - the hour on which X was observed
def computeLeave1Stats(s_x, s_xxt, count, x, weekday, hour):
	if(allNonzero(x)):
		#update the grouped statistics to not include X (subtract it from the sums)
		new_s_x = s_x[weekday, hour] - x
		new_s_xxt = s_xxt[weekday, hour] - x * transpose(x)
		new_count = count[weekday, hour] - 1
	else:
		#If x has a zero, then it was not included in the sums - leave them as is
		new_s_x = s_x[weekday, hour]
		new_s_xxt = s_xxt[weekday, hour]
		new_count = count[weekday, hour]
	
	#compute the mean from these new sums
	mu = new_s_x / new_count
	
	#var(x) = E[x**2] - E[x]**2.  Multiply by n/(n-1) for unbiased covariance correction
	sigma = (new_s_xxt / new_count - mu * transpose(mu)) * (new_count / (new_count - 1))
	
	#Return the mean and covariance matrix
	return (mu, sigma)


#Temporary
def scale_kern_timeseries(kern_timeseries):
	max_val = defaultdict(lambda : float('-inf'))
	
	val_list = defaultdict(list)
	for (date, hour, weekday) in kern_timeseries:
		p = kern_timeseries[date, hour, weekday]
		val_list[weekday, hour].append(p)
		if(p < 0):
			max_val[weekday, hour] = max(max_val[weekday, hour], p)
	
	#pickle.dump(val_list, open("misc_code/val_list.pickle", "w"))
		
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
	(pace_timeseries, pace_grouped) = readPaceData(inDir)
	
	
	
	
		

	logMsg("Computing grouped stats")
	groupedStats = computeGroupedStats(pace_grouped)
	
		
	logMsg("Starting Processes")
	#Use a pool to compute the probabilities in parallel
	pool = Pool(NUM_PROCESSORS)
	sliceIterator = makeSlices(pace_timeseries, pace_grouped, groupedStats, NUM_PROCESSORS) #Iterator breaks the data into slices
	

	outputList = map(generateTimeSlice, sliceIterator) #Run all of the slices in parallel
	#outputList is a list of tuples of incomplete dictionaries - they need to be merged in order to have complete dictionaries
	
	logMsg("Merging outputs")
	#Merge the results from the multiple processes
	(full_timeseries, ind_timeseries, kern_timeseries, zscore_timeseries) = mergeOutputs(outputList)
	

	#temporary...
	if(COMPUTE_KERNEL):
		scale_kern_timeseries(kern_timeseries)
		
	
	logMsg("Writing")
	#Also read the global pace file
	global_pace_timeseries = readGlobalPace(inDir)
	(expected_pace_timeseries, sd_pace_timeseries) = getExpectedPace(global_pace_timeseries)
	
	#Open file to store probability outputs
	lnl_writer = csv.writer(open(OUT_PROB_FILE, "w"))
	lnl_writer.writerow(['date','hour','weekday','full_lnl', 'ind_lnl', 'kern_lnl' ,'global_pace', 'expected_pace', 'sd_pace'])
	
	#Also open file to store the standardized pace vector (zscores)
	zscore_writer = csv.writer(open(OUT_ZSCORE_FILE, "w"))
	zscore_writer.writerow(['Date','Hour','Weekday','E-E','E-U','E-M','E-L','U-E','U-U','U-M','U-L','M-E','M-U','M-M','M-L','L-E','L-U','L-M','L-L'])

	
	#Iterate through the timeseries in order
	for (date, hour, weekday) in sorted(pace_timeseries):
		#Get the 3 different types of probabilities
		full = full_timeseries[(date,hour,weekday)]
		ind = ind_timeseries[(date,hour,weekday)]
		kern = kern_timeseries[date, hour,weekday]
		
		#Also get global pace information
		gl_pace = global_pace_timeseries[(date, hour, weekday)]
		exp_pace = expected_pace_timeseries[(date, hour, weekday)]
		sd_pace = sd_pace_timeseries[(date, hour, weekday)]
		
		#Write the probability stuff
		lnl_writer.writerow([date, hour, weekday, full, ind, kern, gl_pace, exp_pace, sd_pace])
		
		zscore_writer.writerow([date, hour, weekday] + zscore_timeseries[date, hour, weekday])

	logMsg("Done.")


if(__name__=="__main__"):
	generateTimeSeriesLeave1("4year_features")