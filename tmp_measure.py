# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 13:25:25 2015

@author: brian


Functions to load link-by-link traffic conditions as vectors, for use in measureOutliers.py
"""
from db_functions import db_main, db_travel_times
from numpy import matrix, zeros
from routing.Map import Map
from tools import DefaultPool, splitList, logMsg


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
    num_obs = defaultdict(float)
    db_main.connect
    db_main.connect('db_functions/database.conf')
    for date in dates:
        curs = db_travel_times.get_travel_times_cursor(date)
        for [begin_node_id, end_node_id, datetime, travel_time, num_trips] in curs:
            num_obs[begin_node_id, end_node_id] += num_trips
    
    db_main.close()
    
    return num_obs
    
    

# Computes the average number of trips/hour over each link of the map, and saves them
# into the database.  Can make use of parallel processing
# Params:
    # dates - a list of datetimes to process.  Link counts will be averaged over all of these
    # pool - an optional multiprocessing Pool, which will be used for parallel processing
def compute_all_link_counts(dates, pool=DefaultPool()):
    # Split the list and compute the link counts of all slices in parallel
    it = splitList(dates, pool._processes)
    num_obs_list = pool.map(compute_link_counts, it)

    # Merge the outputs by summing each link count
    merged_num_obs = defaultdict(float)
    for num_obs in num_obs_list:
        for key in num_obs:
            merged_num_obs[key] += num_obs[key]

    # Divide the sums by the total number of dates, in order to get the average
    for key in merged_num_obs:
        merged_num_obs[key] /= len(dates)
    
    logMsg("Creating")
    db_travel_times.create_link_counts_table()
    logMsg("Saving")
    db_travel_times.save_link_counts(merged_num_obs)

# Determines the set of links that consistantly have many trips on them.  Specifically,
# we want to keep links that have a high number of trips / hour.  These average link counts
# come from the database table link_counts, which is created by compute_all_link_counts()
# Params:
    # dates - the dates that we want to analyze for obtaining the consistent link set
    # num_trips_threshold - only linkt hat have at least this many trips/hour will be kept
# Returns:
    # a list of links, which are represented by tuples (origin_node_id, connecting_node_id)
def load_consistent_link_set(dates, num_trips_threshold):
    cur = db_travel_times.get_link_counts_cursor()

    consistent_links = [(begin_node_id, end_node_id) for
        (begin_node_id, end_node_id, avg_num_trips) in cur
        if avg_num_trips >= num_trips_threshold]
    return consistent_links





def load_pace_vectors(dates, consistent_link_set):
    # Map (begin_node,connecting_node) --> ID in the pace vector
    link_id_map = defaultdict(lambda : -1) # -1 indicates an invalid ID number    
    for i in xrange(len(consistent_link_set)):
        key = consistent_link_set[i]
        link_id_map[key] = i
        
    db_main.connect('db_functions/database.conf')
    vects = []
    for date in dates:
        # Initialize to zero
        vect = matrix(zeros((len(consistent_link_set), 1)))
        
        # Get the travel times for this datetime
        curs = db_travel_times.get_travel_times_cursor(date)
        
        # Assign travel times into the vector, if this link is in the consistant link set
        for (begin_node_id, end_node_id, datetime, travel_time, num_trips) in curs:
            i = link_id_map[begin_node_id, end_node_id] # i will be -1 if the link is not in the consistant link set
            if(i>=0):
                vect[i] = travel_time
        vects.append(vect)
    
    db_main.close()
    return vects



# Loads link-level travel times into vectors.  Each vector represents a point in time, and
# the dimension of these vectors is equal to the size of the consistent link set
# (the links that consistently have a lot of trips on them)
# Params:
    # num_trips_threshold - Used to determine the consistent link set
# Returns:
    # a list of Numpy column vectors, each element of these vectors represents
    # the travel time on a specific link of the road network
def load_pace_data(num_trips_threshold=20, pool=DefaultPool()):
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Connect to the database adn get hte available dates
    db_main.connect('db_functions/database.conf')
    dates = db_travel_times.get_available_dates()
    
    #logMsg ("Computing consistent link set")
    #compute_all_link_counts(dates, pool=pool)
    
    logMsg("Loading consistent link set")
    consistent_link_set = load_consistent_link_set(dates, num_trips_threshold)
    
    db_main.close()
    
    
    
    logMsg("Generating vectors")

    #Initialize dictionaries    
    pace_timeseries = {}
    pace_grouped = defaultdict(list)
    dates_grouped = defaultdict(list)


    # Split the dates into several pieces and use parallel processing to load the
    # vectors for each of these dates
    it = splitList(dates, pool._processes)
    load_pace_vectors_consistent = partial(load_pace_vectors, consistent_link_set=consistent_link_set)
    list_of_lists = pool.map(load_pace_vectors_consistent, it)
    
    logMsg("Merging outputs.")
    # Flatten the vectors into one big list
    vects = [vect for lst in list_of_lists for vect in lst]
    
    # Loop through all dates - one vector will be created for each one
    for i in xrange(len(dates)):
        date = dates[i]
        vect = vects[i]
      
        
        # Extract the date, hour of day, and day of week
        just_date = str(date.date())
        hour = date.hour
        weekday = weekday_names[date.weekday()]
        
        #Save vector in the timeseries
        pace_timeseries[(just_date, hour, weekday)] = vect
        
        #save the vector into the group
        pace_grouped[(weekday, hour)].append(vect)
        dates_grouped[(weekday, hour)].append(just_date)
    
    
    # Assign trip names based on node ids
    trip_names = ["%d-->%d"%(start, end) for (start, end) in consistent_link_set]
            
    return (pace_timeseries, pace_grouped, dates_grouped, trip_names)







# Debug method that draws the roadmap as a figure
def drawFigure(filename, road_map, num_obs):
    logMsg("Writing " + filename)
    with open(filename, 'w') as f:
        csvw = csv.writer(f)
        csvw.writerow(['begin_node','end_node', 'begin_lat', 'begin_lon', 
                       'end_lat', 'end_lon', 'avg_num_trips'])
                       
        for begin_node_id, end_node_id in sorted(num_obs, key= lambda x: num_obs[x], reverse=True):
            
            if((begin_node_id, end_node_id) in road_map.links_by_node_id):
                begin_node = road_map.nodes_by_id[begin_node_id]
                end_node = road_map.nodes_by_id[end_node_id]
                csvw.writerow([begin_node_id, end_node_id, begin_node.lat, begin_node.long,
                                   end_node.lat, end_node.long, num_obs[begin_node_id, end_node_id]])


def test():

    
    db_main.connect('db_functions/database.conf')
    
    curs = db_main.execute("select distinct datetime from travel_times where datetime>= '2012-06-17' and datetime < '2012-06-24' order by datetime;")
    #curs = db_main.execute("select distinct datetime from travel_times where datetime>= '2013-01-01' and datetime < '2013-01-02' order by datetime;")
    
    
    
    dates = [date for (date,) in curs]
    print ("Found %d dates" % len(dates))
    
    get_consistent_link_set(dates)
