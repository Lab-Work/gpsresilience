# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 15:18:52 2015

@author: brian
"""

from eventDetection import keyFromDatetime, computeEventProperties, readOutlierScores, readZScoresTimeseries
from measureOutliers import readGlobalPace, getExpectedPace
from tools import logMsg, getQuantile, dateRange

from datetime import datetime, timedelta
import csv



def crossesThreshold(start_date, end_date, mahal_timeseries, threshold):
    for key in [keyFromDatetime(d) for d in dateRange(start_date, end_date, timedelta(hours=1))]:
        if(key in mahal_timeseries and mahal_timeseries[key] > threshold):
            return True



def detectWindowedEvents(mahal_timeseries, zscore_timeseries, global_pace_timeseries, 
                          out_file, window_size=6, threshold_quant=.95):
                              
    logMsg("Detecting events at %d%% bound" % int(threshold_quant*100))
                              
    #Sort the keys of the timeseries chronologically    
    sorted_dates = sorted(mahal_timeseries)
    
    #Generate the list of values of R(t)
    mahal_list = [mahal_timeseries[d] for d in sorted_dates]

    
    #Use the quantile to determine the threshold
    sorted_mahal = sorted(mahal_list)
    threshold = getQuantile(sorted_mahal, threshold_quant)

    # Get the expected global pace    
    (expected_pace_timeseries, sd_pace_timeseries) = getExpectedPace(global_pace_timeseries)        
    
    
    
    start_date = datetime(2010,1,1)
    end_date = datetime(2014,1,1)
    shift = timedelta(hours=window_size)
    
    prev_above_threshold = False
    current_event_start = None
    current_event_end = None
    eventList = []
    for date in dateRange(start_date, end_date, shift):
        #print
        #print(str(date))
        #print(prev_above_threshold)
        if(crossesThreshold(date, date+shift, mahal_timeseries, threshold)):
            #print("CROSS")
            if(not prev_above_threshold):
                #print("RESET")
                current_event_start = date
                
            current_event_end = date+shift
            prev_above_threshold=True
        else:
            if(prev_above_threshold):
                #print("*************OUTPUTTING************")
                #print("%s -> %s" % (current_event_start, current_event_end))
                start_key = keyFromDatetime(current_event_start)
                end_key = keyFromDatetime(current_event_end)
                event = computeEventProperties(start_key, end_key, mahal_timeseries, 
                                           global_pace_timeseries, expected_pace_timeseries,
                                           zscore_timeseries, sorted_mahal=sorted_mahal,
                                           mahal_threshold=threshold)
                #Add to list            
                eventList.append(event)
                
            prev_above_threshold =False
    
    #Sort events by duration, in descending order
    eventList.sort(key = lambda x: x[5], reverse=True)
    
    #Write events to a CSV file
    w = csv.writer(open(out_file, "w"))
    w.writerow(["start_date", "end_date", "max_mahal", "mahal_quant", "duration", "hours_above_thresh", "max_pace_dev",
                "min_pace_dev", "worst_trip"])
                
    for event in eventList:
        [start_date, end_date, max_mahal, mahal_quant, duration, hours_above_thresh, max_pace_dev, min_pace_dev, worst_trip] = event
        formattedEvent = [start_date, end_date, "%.2f" % max_mahal, "%.3f" % mahal_quant, 
                          duration, hours_above_thresh, "%.2f" % max_pace_dev,
                          "%.2f" % min_pace_dev, worst_trip]
        w.writerow(formattedEvent)
    
    return eventList
        
    

def getEventDuration(events, dateStr):
    for event in events:
        [start_date, end_date, max_mahal, mahal_quant, duration, hours_above_thresh,
        max_pace_dev, min_pace_dev, worst_trip] = event
             
        if(str(start_date) <= dateStr and str(end_date) >= dateStr):
            return duration
    return 0

def performEventDurationTest():
    mahal_timeseries = readOutlierScores("results/outlier_scores.csv")
    global_pace_timeseries = readGlobalPace("4year_features")
    zscore_timeseries = readZScoresTimeseries("results/zscore.csv")
    
    mahal_timeseries_fine = readOutlierScores("results/link_20_normalize_outlier_scores.csv")
    
    threshold_vals = [.90,.91,.92,.93,.94,.95,.96,.97,.98,.99]
    window_sizes = [1,2,3,4,6,8,12,24]
    with open('results/threshold_experiment.csv', 'w') as f:
        w = csv.writer(f)
        w.writerow(['granularity', 'window','threshold', 'duration'])
        
        for window_size in window_sizes:
            for threshold in threshold_vals:
                print (window_size, threshold)
                events = detectWindowedEvents(mahal_timeseries, zscore_timeseries, global_pace_timeseries, 
                      "results/events_windowed.csv", window_size=window_size, threshold_quant=threshold)
                duration = getEventDuration(events, "2012-10-31")
                w.writerow(["coarse", window_size, threshold, duration])
    
    
                events= detectWindowedEvents(mahal_timeseries_fine, zscore_timeseries, global_pace_timeseries, 
                    "results/link_20_normalize_events_windowed.csv", window_size=window_size,
                    threshold_quant=threshold)      
                duration = getEventDuration(events, "2012-10-31")
                w.writerow(["fine", window_size, threshold, duration])
                          
                




if(__name__=="__main__"):
    #performEventDurationTest()    
    
    mahal_timeseries = readOutlierScores("results/outlier_scores.csv")
    global_pace_timeseries = readGlobalPace("4year_features")
    zscore_timeseries = readZScoresTimeseries("results/zscore.csv")
    detectWindowedEvents(mahal_timeseries, zscore_timeseries, global_pace_timeseries, 
                          "results/events_windowed.csv", window_size=8, threshold_quant=.95)
    
    mahal_timeseries = readOutlierScores("results/link_20_normalize_outlier_scores.csv")
    global_pace_timeseries = readGlobalPace("4year_features")
    zscore_timeseries = readZScoresTimeseries("results/zscore.csv")
    detectWindowedEvents(mahal_timeseries, zscore_timeseries, global_pace_timeseries, 
                          "results/link_20_normalize_events_windowed.csv", window_size=8,
                          threshold_quant=.95)                  
                          
                          
    logMsg("done")