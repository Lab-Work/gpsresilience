# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 13:25:25 2015

@author: brian


Functions to load link-by-link traffic conditions as vectors, for use in measureOutliers.py
"""
from db_functions import db_main, db_travel_times
from numpy import matrix, zeros
# # from routing.Map import Map
from tools import DefaultPool, splitList, logMsg, dateRange
from datetime import datetime
import pickle

from multiprocessing import Pool
from collections import defaultdict
from functools import partial
import csv


# Computes the total number of trips/hour over each link of the map, and returns
# them in a dictionary
# Params:
    # dates - a list of dates to process
# Returns:
    # num_obs - a dictionary that maps (begin_node_id, end_node_id) --> total number of trips
def compute_link_counts(dates):
    num_appearances = defaultdict(float)
    db_main.connect('db_functions/database.conf')
    for date in dates:
        curs = db_travel_times.get_travel_times_cursor_new(date)
        for [link_id, date_time, paces, num_cars] in curs:
            num_appearances[link_id] += 1
    
    db_main.close()
    
    return num_appearances
    
    

# Computes the average number of trips/hour over each link of the map, and saves them
# into the database.  Can make use of parallel processing
# Params:
    # dates - a list of datetimes to process.  Link counts will be averaged over all of these
    # pool - an optional multiprocessing Pool, which will be used for parallel processing
def compute_all_link_counts(dates, pool=DefaultPool()):
    # Split the list and compute the link counts of all slices in parallel
    it = splitList(dates, pool._processes)
    num_obs_list = pool.map(compute_link_counts, it)
    # print "1", num_obs_list[0]
    # Merge the outputs by summing each link count
    merged_count_obs = defaultdict(float)
    for num_appearances in num_obs_list:
        for key in num_appearances:
            merged_count_obs[key] += num_appearances[key]

    # Divide the sums by the total number of dates, in order to get the average
    for key in merged_count_obs:
        merged_count_obs[key] /= len(dates)
    
    print "keys", len(merged_count_obs.keys())
    db_main.connect('db_functions/database.conf')
    logMsg("Creating")
    db_travel_times.create_link_counts_table_new()
    logMsg("Saving")
    # Issue of num of arguments
    db_travel_times.save_link_counts_new(merged_count_obs)


# Determines the set of links that consistantly have many trips on them.  Specifically,
# we want to keep links that have a high number of trips / hour.  These average link counts
# come from the database table link_counts, which is created by compute_all_link_counts()
# Params:
    # dates - the dates that we want to analyze for obtaining the consistent link set
    # perc_obs_threshold - only links that have a measurement at least this much of the time will be returned
# Returns:
    # a list of links, which are represented by tuples (origin_node_id, connecting_node_id)
def load_consistent_link_set(dates, perc_obs_threshold):
    cur = db_travel_times.get_link_counts_cursor_new()

    consistent_links = [link_id for
        (link_id, perc_obs) in cur
        if perc_obs >= perc_obs_threshold]
    return consistent_links



# Loads a list of pace vectors, which correspond to link paces at a given time.
# Params:
    # dates - the dates to load pace vectors for
    # consistent_link_set - a list of (origin_node_id, dest_node_id) tuples, which each
        # represent a link in the graph.  These are the links which will be used to
        # build the pace vectors (in the same order)
# Returns:
    # vects - a list of vectors in the same order as the dates
def load_pace_vectors(dates, consistent_link_set):
    # Map (begin_node,connecting_node) --> ID in the pace vector
    link_id_map = defaultdict(lambda : -1) # -1 indicates an invalid ID number    
    for i in xrange(len(consistent_link_set)):
        # print i
        key = consistent_link_set[i]
        # print long(key)
        key = long(key)
        link_id_map[key] = i
        
    db_main.connect('db_functions/database.conf')
    vects = []
    weights = []
    for date in dates:
        # Initialize to zero
        # print date
        vect = matrix(zeros((len(consistent_link_set), 1)))
        weight = matrix(zeros((len(consistent_link_set), 1)))
        
        
        # Get the travel times for this datetime
        curs = db_travel_times.get_travel_times_cursor_new(date)
        # Assign travel times into the vector, if this link is in the consistant link set
        for (link_id, date_time, paces, num_cars) in curs:
            # print (link_id, date_time, paces, num_cars)
            # print "link_id",link_id
            i = link_id_map[link_id] # i will be -1 if the link is not in the consistant link set
            if(i>=0):
                vect[i] = paces
                weight[i] = num_cars
        vects.append(vect)
        weights.append(weight)
    db_main.close()
    return vects, weights



# Loads link-level travel times into vectors.  Each vector represents a point in time, and
# the dimension of these vectors is equal to the size of the consistent link set
# (the links that consistently have a lot of trips on them).  Can use parallel processing
# to significantly boost performance
# Params:
    # num_trips_threshold - Used to determine the consistent link set
# Returns:
    # a list of Numpy column vectors, each element of these vectors represents
    # the travel time on a specific link of the road network
def load_pace_data(perc_data_threshold, pool=DefaultPool()):
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Connect to the database adn get hte available dates
    logMsg ("Getting relevant dates.")
    db_main.connect('db_functions/database.conf')
    # dates = db_travel_times.get_available_dates()
    dates = list(dateRange(datetime(2014,06,01), datetime(2014,07,01)))
    
    ''' Only Do Once for the whole dataset and store in link_counts_chicago table'''
    #logMsg ("Computing consistent link set")
    #compute_all_link_counts(dates, pool=pool)
    
    logMsg("Loading consistent link set")
    consistent_link_set = load_consistent_link_set(dates, perc_data_threshold)
    if len(consistent_link_set) == 0:
        logMsg("Find 0 consistent_links. Return.")
        return
    else:
        print("len of consistent_link_set", len(consistent_link_set))
    db_main.close()
    
    logMsg("Generating vectors")

    #Initialize dictionaries    
    pace_timeseries = {}
    pace_grouped = defaultdict(list)
    dates_grouped = defaultdict(list)
    weights_grouped = defaultdict(list)


    # Split the dates into several pieces and use parallel processing to load the
    # vectors for each of these dates.  We will use a partial function to hold the
    # consistent_link_set constant across all dates
    it = splitList(dates, pool._processes)
    load_pace_vectors_consistent = partial(load_pace_vectors, consistent_link_set=consistent_link_set)
    list_of_lists = pool.map(load_pace_vectors_consistent, it)
    
    logMsg("Merging outputs.")
    # Flatten the vectors into one big list
    vects = [vect for vect_lst, weight_lst in list_of_lists for vect in vect_lst]
    weights = [weight for vect_lst, weight_lst in list_of_lists for weight in weight_lst]
    
    # Loop through all dates - one vector will be created for each one
    for i in xrange(len(dates)):
        date = dates[i]
        vect = vects[i]
        weight = weights[i]
      
        
        # Extract the date, hour of day, and day of week
        just_date = str(date.date())
        hour = date.hour
        weekday = weekday_names[date.weekday()]
        
        #Save vector in the timeseries
        
        
        #save the vector into the group
        # pace_grouped[(weekday, hour)].append(vect)
        # weights_grouped[(weekday, hour)].append(weight)
        # dates_grouped[(weekday, hour)].append(just_date)

        # use constant as key for this moment
        # weekday = 0
        # hour = 0
        # print just_date
        pace_timeseries[(just_date, hour, weekday)] = vect
        # print "vect here =========", vect
        pace_grouped[(weekday, hour)].append(vect)
        weights_grouped[(weekday, hour)].append(weight)
        dates_grouped[(weekday, hour)].append(just_date)


    
    # print pace_timeseries.keys()
    print len(pace_grouped[(0,0)]), len(pace_grouped[(0,0)][0])
    # Assign trip names based on node ids
    trip_names = ["%d" % link_id for link_id in consistent_link_set]
    
    # print "    len", len(pace_grouped.values())
    return (pace_timeseries, pace_grouped, weights_grouped, dates_grouped,
                trip_names, consistent_link_set)

def load_from_file(pickle_filename):
    with open(pickle_filename, 'r') as f:
        data = pickle.load(f)
    
    (pace_timeseries, pace_grouped, weights_grouped, dates_grouped,
                trip_names, consistent_link_set) = data
    return (pace_timeseries, pace_grouped, weights_grouped, dates_grouped,
                trip_names, consistent_link_set)

def test():
    pool = Pool(4)

    print("Connecting")
    db_main.connect('db_functions/database.conf')
    
    print("Loading Pace Data")
    data = load_pace_data(perc_data_threshold=.6, pool=pool)
    with open('tmp_vectors_chi_1_group.pickle', 'w') as f:
        pickle.dump(data, f)


# def debug():
#     (pace_timeseries, pace_grouped, weights_grouped, dates_grouped,
#                 trip_names, consistent_link_set) = load_from_file('tmp_vectors.pickle')
#     for elem in pace_grouped.keys():
#         # print pace_grouped[elem]
#         break


if(__name__=="__main__"):
    test()
    # debug()

