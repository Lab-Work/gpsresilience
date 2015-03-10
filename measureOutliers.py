# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 12:34:53 2014

@author: brian
"""
import numpy
from numpy import matrix, transpose
import os, csv
from collections import defaultdict
from multiprocessing import Pool

from mahalanobis import *
from traffic_estimation.plot_estimates import make_video, build_speed_dicts
from lof import *
from tools import *

from measureLinkOutliers import load_pace_data

NUM_PROCESSORS = 8


#Reads time-series pace data from a file, and sorts it into a convenient format.
#Arguments:
    #dirName - the directory which contains time-series features (produced by extractGridFeatures.py)
#Returns:  (pace_timeseries, var_timeseries, count_timeseries, pace_grouped).  Breakdown:
    #pace_timeseries - a dictionary which maps (date, hour, weekday) to the corresponding average pace vector (average pace of each trip type)
    #var_timeseries - a dictionary which maps (date, hour, weekday) to the corresponding pace variance vector (variance of paces of each trip type)
    #count_timeseries - a dictionary which maps (date, hour, weekday) to the corresponding count vector (number of occurrences of each trip type)
    #pace_grouped - a dictionary which maps (weekday, hour) to the list of corresponding pace vectors
    #        for example, ("Wednesday", 5) maps to the list of all pace vectors that occured on a Wednesday at 5am.
    #trip_names - the names of the trips, which correspond to the dimensions in the vectors (e.g. "E-E")
def readPaceData(dirName):
    logMsg("Reading files from " + dirName + " ...")
    #Create filenames
    paceFileName = os.path.join(dirName, "pace_features.csv")

    
    #Initialize dictionaries    
    pace_timeseries = {}
    pace_grouped = defaultdict(list)
    dates_grouped = defaultdict(list)
    
    #Read the pace file
    r = csv.reader(open(paceFileName, "r"))
    header = r.next()
    colIds = getHeaderIds(header)
    
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
        
        #save the vector into the group
        pace_grouped[(weekday, hour)].append(v)
        dates_grouped[(weekday, hour)].append(date)

    trip_names = header[3:]
    
    #return time series and grouped data
    return (pace_timeseries, pace_grouped, dates_grouped, trip_names)





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
    
    
    
#Given a pace timeseries, compute the expected value for each timeslice (based on the weekly periodic pattern)
#This is a leave-one-out estimate (e.g. The expected pace for Friday, January 1st at 8am is the average of all Fridays at 8am EXCEPT for Friday January 1st)
#Arguments:
	#global_pace_timeseries - see likelihood_test_parallel.readGlobalPace()
#Returns:
	#A tuple (expected_pace_timeseries, sd_pace_timeseries).  Breakdown:
		#expected_pace_timeseries - A dictionary keyed by (date, hour, weekday) which contains expected paces for each hour of the timeseries
		#expected_pace_timeseries - A dictionary keyed by (date, hour, weekday) which contains the standard deviation of paces at that hour of the time series
def getExpectedPace(global_pace_timeseries):
	#First computed grouped counts, sums, and sums of squares
	#Note that these are leave-one-IN estimates.  This will be converted to leave-one-out in the next step
	grouped_sum = defaultdict(float)
	grouped_ss = defaultdict(float)	
	grouped_count = defaultdict(float)
	#Iterate through all days, updating the corresponding sums
	for (date, hour, weekday) in global_pace_timeseries:
		grouped_sum[weekday, hour] += global_pace_timeseries[date,hour,weekday]
		grouped_ss[weekday, hour] += global_pace_timeseries[date,hour,weekday] ** 2
		
		grouped_count[weekday, hour] += 1
	
	expected_pace_timeseries = {}
	sd_pace_timeseries = {}
	#Now that the grouped stats are computed, iterate through the timeseries again
	for (date, hour, weekday) in global_pace_timeseries:
		#The updated count, sum, and sum of squares are computed by subtracting the observation at hand
		#i.e. a leave-one-out estimate
		updated_sum = grouped_sum[weekday, hour] - global_pace_timeseries[date, hour, weekday]
		updated_ss = grouped_ss[weekday, hour] - global_pace_timeseries[date, hour, weekday] ** 2
		updated_count = grouped_count[weekday, hour] - 1
		
		#Compute the average and standard deviation from these sums
		expected_pace_timeseries[date, hour, weekday] = updated_sum / updated_count
		sd_pace_timeseries[date, hour, weekday] = sqrt((updated_ss / updated_count) - expected_pace_timeseries[date, hour, weekday] ** 2)
	
	#Return the computed time series dictionaries
	return (expected_pace_timeseries, sd_pace_timeseries)    
    
    
#Computes the outlier scores for all of the mean pace vectors in a given weekday/hour pair (for example Wednesdays at 3pm)
#Many of these can be run in parallel
#params:
    #A tuple (paceGroup, dateGroup, hour, weekday) - see groupIterator()
#returns:
    #A list of tuples, each of which contain various types of outlier scores for each date
def processGroup((paceGroup, weightGroup, dateGroup, hour, weekday, diag, normalize)):
    #logMsg("Processing " + weekday + " " + str(hour))
    
    #Compute mahalanobis outlier scores
    (mahals, group_zscores) = computeMahalanobisDistances(paceGroup, independent=diag,
                                                        group_of_weights=weightGroup,
                                                        normalize=normalize)
    
    #compute local outlier factors with various k parameters
    lofs1 = getLocalOutlierFactors(paceGroup, 1)
    lofs3 = getLocalOutlierFactors(paceGroup, 3)
    lofs5 = getLocalOutlierFactors(paceGroup, 5)
    lofs10 = getLocalOutlierFactors(paceGroup, 10)
    lofs20 = getLocalOutlierFactors(paceGroup, 20)
    lofs30 = getLocalOutlierFactors(paceGroup, 30)
    lofs50 = getLocalOutlierFactors(paceGroup, 50)

    #A dictionary which maps (date, hour, weekday), to an entry
    #An entry is a tuple that contains various types of outlier scores
    scores = {}
    #Here, each entry is the zscored vector
    zscores = {}
    for i in range(len(paceGroup)):
        entry = (mahals[i], lofs1[i], lofs3[i], lofs5[i], lofs10[i], lofs20[i], lofs30[i], lofs50[i])
        scores[dateGroup[i], hour, weekday] = entry
        
        zscores[dateGroup[i], hour, weekday] = group_zscores[i]
    #Return the scores
    return (scores, zscores)

#An iterator which supplies inputs to processGroup()
#Each input contains a set of mean pace vectors, and some extra time info
#params:
    #pace_grouped - Lists of vectors, indexed by weekday/hour pair - see readPaceData()
    #date_grouped - Date strings, indexd by weekday/hour pair - see readPaceData()
def groupIterator(pace_grouped, weights_grouped, dates_grouped, diag=False, normalize=False):
    #Iterate through weekday/hour pairs
    for (weekday, hour) in pace_grouped:
        #Grab the list of vectors
        paceGroup = pace_grouped[weekday, hour]
        #grab the list of dates
        dateGroup = dates_grouped[weekday, hour]
        
        if(weights_grouped is None):
            weightGroup = None
        else:
            weightGroup = weights_grouped[weekday, hour]
            
        #Each output contains these lists, as well as the hour and day of week
        yield (paceGroup, weightGroup, dateGroup, hour, weekday, diag, normalize)

#Merges many group scores - see the output of processGroup() - into one
#params:
    #outputList - a list of (score, zscore) tuples
    #Each element of the list is an output of processGroup()
#return:
    #scores - a dictionary that maps date/hour pairs to entries
    #zscores - a dictionary that maps date/hour pairs to zscores
def reduceOutputs(outputList):
    scores = {}
    zscores = {}
    for (score, zscore) in outputList:
        scores.update(score)
        zscores.update(zscore)
        
    return (scores, zscores)
    

#Generates time-series log-likelihood values
#Similar to generateTimeSeries(), but LEAVES OUT the current observation when computing the probability
#These describe how likely or unlikely the state of the city is, given the distribution of "similar"
# days (same hour and day of week) but not today.
#Params:
    #inDir - the directory which contains the time-series feature files (CSV format)
    #use_link_db - if True, will use link-by-link travel times from the DB.
        # If False, will use aggregated info from OD region pairs
    #returns - no return value, but saves files into results/...
def generateTimeSeriesLeave1(inDir, use_link_db=False, consistent_threshold=50, 
                             use_feature_weights=False, normalize=False, make_zscore_vid=False):
    
    pool = Pool(NUM_PROCESSORS) #Prepare for parallel processing
    #pool = DefaultPool()

    numpy.set_printoptions(linewidth=1000, precision=4)
    
    #Read the time-series data from the file
    logMsg("Reading files...")
    if(use_link_db):
        file_prefix = "link_%d_" % consistent_threshold
        if(use_feature_weights):
            file_prefix += "weighted_"
        
        if(normalize):
            file_prefix += "normalize_"
        
        pace_timeseries, pace_grouped, weights_grouped, dates_grouped, trip_names, consistent_link_set = load_pace_data(
            num_trips_threshold=consistent_threshold, pool=pool)
            
        if(use_feature_weights==False):
            weights_grouped = None
    else:
        file_prefix = "coarse_"
        (pace_timeseries, pace_grouped, dates_grouped, trip_names) = readPaceData(inDir)
        weights_grouped = None

    #Also get global pace information
    global_pace_timeseries = readGlobalPace(inDir)
    (expected_pace_timeseries, sd_pace_timeseries) = getExpectedPace(global_pace_timeseries)

    logMsg("Starting processes")

    
    #Iterator breaks the data into groups
    gIter = groupIterator(pace_grouped, weights_grouped, dates_grouped,
                          diag=use_link_db, normalize=normalize)
                          
    
    outputList = pool.map(processGroup, gIter) #Run all of the groups, using as much parallel computing as possible

    logMsg("Merging output")
    #Merge outputs from all of the threads
    (outlierScores, zscores) = reduceOutputs(outputList)

    
    logMsg("Writing file")
    #Output outlier scores to file
    scoreWriter = csv.writer(open("results/%soutlier_scores.csv"%file_prefix, "w"))
    scoreWriter.writerow(['date','hour','weekday', 'mahal', 'lof1', 'lof3', 'lof5', 'lof10', 'lof20', 'lof30', 'lof50' ,'global_pace', 'expected_pace', 'sd_pace'])
    

    for (date, hour, weekday) in sorted(outlierScores):
        gl_pace = global_pace_timeseries[(date, hour, weekday)]
        exp_pace = expected_pace_timeseries[(date, hour, weekday)]
        sd_pace = sd_pace_timeseries[(date, hour, weekday)]
        
        (scores) = outlierScores[date, hour, weekday]
        
        scoreWriter.writerow([date, hour, weekday] + list(scores) + [gl_pace, exp_pace, sd_pace])


    zscoreWriter= csv.writer(open("results/%szscore.csv"%file_prefix, "w"))
    zscoreWriter.writerow(['Date','Hour','Weekday'] + trip_names)
    #Output zscores to file
    for (date, hour, weekday) in sorted(zscores):
        std_vect = zscores[date, hour, weekday]
        zscoreWriter.writerow([date, hour, weekday] + ravel(std_vect).tolist())


    #def make_video(tmp_folder, filename_base, pool=DefaultPool(), dates=None, speed_dicts=None)
    if(make_zscore_vid):
        logMsg("Making speed dicts")
        #zscore_list = [zscores[key] for key in sorted(zscores)]
        date_list = dates = [datetime(2012,10,21) + timedelta(hours=1)*x for x in range(168*3)]
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']        
        zscore_list = [zscores[str(d.date()), d.hour, weekday_names[d.weekday()]] for d in date_list]

        speed_dicts = build_speed_dicts(consistent_link_set, zscore_list)
        logMsg("Making video")
        make_video("tmp_vid", "zscore_vid", pool=pool, dates=date_list, speed_dicts=speed_dicts)
        
        
        

    logMsg("Done.")
    
    pool.close()

if(__name__=="__main__"):
    #logMsg("Running raw analysis")
    #generateTimeSeriesLeave1("4year_features", use_link_db=True)
    
    """
    logMsg("Running normalized analysis")
    generateTimeSeriesLeave1("4year_features", use_link_db=True, normalize=True)
    
    logMsg("Running weighted analysis")
    generateTimeSeriesLeave1("4year_features", use_link_db=True, use_feature_weights=True, normalize=True)
    """
    
    logMsg("Running normalized analysis")
    generateTimeSeriesLeave1("4year_features", use_link_db=True, normalize=True, consistent_threshold=20)
    
    logMsg("Running weighted analysis")
    generateTimeSeriesLeave1("4year_features", use_link_db=True, use_feature_weights=True, normalize=True, consistent_threshold=20)

    logMsg("Running normalized analysis")
    generateTimeSeriesLeave1("4year_features", use_link_db=True, normalize=True, consistent_threshold=300)
    
    logMsg("Running weighted analysis")
    generateTimeSeriesLeave1("4year_features", use_link_db=True, use_feature_weights=True, normalize=True, consistent_threshold=300)

