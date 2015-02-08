# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 13:25:25 2015

@author: brian


Functions to load link-by-link traffic conditions as vectors, for use in measureOutliers.py
"""
from db_functions import db_main, db_travel_times
from numpy import matrix, zeros
from routing.Map import Map

from collections import defaultdict
import csv





# Computes the average number of trips/hour over each link of the map, then saves
# these counts in the database.
# Params:
    # dates - a list of dates to average over
def compute_link_counts(dates):
    num_obs = defaultdict(float)
    for date in dates:
        curs = db_travel_times.get_travel_times_cursor(date)
        for [begin_node_id, end_node_id, datetime, travel_time, num_trips] in curs:
            num_obs[begin_node_id, end_node_id] += num_trips
    
    for key in num_obs:
        num_obs[key] /= len(dates)
    
    print("Creating")
    db_travel_times.create_link_counts_table()
    print("Saving")
    db_travel_times.save_link_counts(num_obs)



# Determines the set of links that consistantly have many trips on them.  Specifically,
# we want to keep links that have a high number of trips / hour.  These average link counts
# come from the database table link_counts, which is created by compute_link_counts()
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
    
# Loads link-level travel times into vectors.  Each vector represents a point in time, and
# the dimension of these vectors is equal to the size of the consistent link set
# (the links that consistently have a lot of trips on them)
# Params:
    # num_trips_threshold - Used to determine the consistent link set
# Returns:
    # a list of Numpy column vectors, each element of these vectors represents
    # the travel time on a specific link of the road network
def load_pace_data(num_trips_threshold=50):
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Connect to the database adn get hte available dates
    db_main.connect('db_functions/database.conf')
    dates = db_travel_times.get_available_dates()
    
    print ("Computing consistent link set")
    compute_link_counts(dates)
    
    print("Loading consistent link set")
    consistent_link_set = load_consistent_link_set(dates, num_trips_threshold)
    
    
    print("Running analysis")
    # Map (begin_node,connecting_node) --> ID in the pace vector
    link_id_map = defaultdict(lambda : -1) # -1 indicates an invalid ID number    
    for i in xrange(len(consistent_link_set)):
        key = consistent_link_set[i]
        link_id_map[key] = i
    

    #Initialize dictionaries    
    pace_timeseries = {}
    pace_grouped = defaultdict(list)
    dates_grouped = defaultdict(list)

    # Loop through all dates - one vector will be created for each one
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
    print("Writing " + filename)
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