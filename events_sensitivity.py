# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 19:40:57 2015

@author: Brian Donovan (briandonovan100@gmail.com)
"""
from datetime import datetime, timedelta
import csv
from tools import logMsg



events_data = [("Snowstorm" , "2010-12-26 13:00:00" , 137),
("Sandy" , "2012-10-28 21:00:00" , 116),
("?" , "2012-11-12 07:00:00" , 110),
("Snowstorm" , "2011-01-31 09:00:00" , 103),
("Snowstorm" , "2011-01-26 09:00:00" , 56),
("Protest?" , "2011-09-18 19:00:00" , 49),
("Irene" , "2011-08-27 11:00:00" , 46),
("Thanksgiving" , "2011-11-22 11:00:00" , 43),
("?" , "2013-10-12 01:00:00" , 43),
("?" , "2013-09-28 08:00:00" , 37)]

events = []
for event in events_data:
    (name, date_str, duration) = event
    start_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    end_date = start_date + timedelta(hours=duration)
    events.append((name, start_date, end_date, duration))



event_durations = {}
#k_vals = [7,8,9,10,15,20,25,30,35,40,45,50]
k_vals = range(7,51)
for k in k_vals:
    event_file = 'results/coarse_events_k%d.csv' % k
    logMsg('Examining %s' % event_file)
    
    for event in events:
        event_durations[event, k] = 0
    
    
    for event in events:
        print (event, k)
        (ev_name, ev_start, ev_end, ev_duration) = event

        for [start_date, end_date, duration, max_mahal, max_pace_dev, min_pace_dev] in events:
            #start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            #end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
            duration = (end_date - start_date).total_seconds() / 3600 + 1
        
        
            if(ev_end > start_date and ev_start < end_date):
                print ("MATCH - %d , %s --> %s" % (duration, str(start_date), str(end_date_str)))
                event_durations[event, k] = max(event_durations[event, k], duration)



with open('results/event_duration_comparison.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(['event', 'num_regions', 'duration'])
    for event in events:
        (name, start_date, end_date, _duration) = event
        event_name = name + ' ' + start_date.strftime('%Y-%m-%d')
        for k in k_vals:
            duration = event_durations[event, k]
            w.writerow([event_name, k, duration])
                    
                
            
