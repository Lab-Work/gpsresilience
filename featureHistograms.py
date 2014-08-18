# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 12:52:31 2014

@author: brian
"""
import csv
from collections import defaultdict
from grid import *
from regions import *
from multiprocessing import Pool



NUM_PROCESSORS = 16

class Histogram:
	def __init__(self, name, granularity, lower_bound=float('-inf'), upper_bound=float('inf')):
		self.name = name
		self.granularity = granularity
		self.lower_bound = lower_bound
		self.upper_bound = upper_bound
		self.counts = defaultdict(int)
	
	def record(self, value):
		
		rounded = int(value/self.granularity)*self.granularity
		
		rounded = max(self.lower_bound, rounded)
		rounded = min(self.upper_bound, rounded)
		
		self.counts[rounded] += 1
	
	def saveToFile(self, filename):
		w = csv.writer(open(filename, 'w'))
		w.writerow([self.name, 'frequency'])
		
		for val in sorted(self.counts):
			w.writerow([val, self.counts[val]])


def mergeHistogramTuples(histTupleList):
	
	#Initialize a tuple of histograms -all counts set to 0
	mergedHistList = []
	for hist in histTupleList[0]: #Mirror the first tuple in the histTupleList
		histCopy =  Histogram(hist.name, hist.granularity, hist.lower_bound, hist.upper_bound)
		mergedHistList.append(histCopy)
	mergedHistTuple = tuple(mergedHistList)
		
	
	#Iterate through all tuples in the list
	for histTuple in histTupleList:
		#Iterate through all histograms in the tuple
		for i in range(len(histTuple)):
			#Update the counts of the appropriate merged Histogram
			#This is performed by summing the values from the smaller histograms
			for val in histTuple[i].counts:
				mergedHistTuple[i].counts[val] += histTuple[i].counts[val]
	
	return mergedHistTuple



def monthIterator():
	for year in range(2010, 2014):
		for month in range(1, 13):
			yield (year, month)


def computeMonth((year, month)):


	hist_lon = Histogram('lon', .01, lower_bound=-80, upper_bound = -70)
	hist_lat = Histogram('lat', .01, lower_bound=35, upper_bound = 45)
	hist_straightline = Histogram('straightline', .01, lower_bound=0, upper_bound = 100)
	hist_time = Histogram('time', 5, lower_bound=0, upper_bound = 10*3600)
	hist_minutes = Histogram('minutes', 60, lower_bound=0, upper_bound = 10*3600)
	hist_dist = Histogram('distance', .1, lower_bound=0, upper_bound = 100)
	hist_miles = Histogram('miles', 1, lower_bound=0, upper_bound = 100)
	hist_winding = Histogram('winding', .01, lower_bound=0, upper_bound = 100)
	hist_pace = Histogram('pace', 5, lower_bound=0, upper_bound = 10*3600)
	
	
	filename = "../new_chron/FOIL" + str(year) + "/trip_data_" + str(month) + ".csv"
	
	logMsg("Reading file " + filename)
	r = csv.reader(open(filename, "r"))
	i = 0
	header = True
	for line in r:
		if(header):
			Trip.initHeader(line)
			header = False
		else:
			try:
				trip = Trip(line)
				
				hist_lon.record(trip.fromLon)
				hist_lon.record(trip.toLon)

				hist_lat.record(trip.fromLat)
				hist_lat.record(trip.toLat)
				
				hist_straightline.record(trip.straight_line_dist)
				
				hist_time.record(trip.time)
				hist_minutes.record(trip.time)
				
				hist_dist.record(trip.dist)
				hist_miles.record(trip.dist)
				
				hist_winding.record(trip.winding_factor)
				
				if(trip.dist > 0):
					hist_pace.record(float(trip.time) / trip.dist)
			except ValueError:
				pass

		i += 1
		if(i%1000000==0):
			logMsg(filename + " read " + str(i) + " rows")



	return (hist_lon, hist_lat, hist_straightline, hist_time, hist_minutes, hist_dist, hist_miles, hist_winding, hist_pace)




logMsg("Computing histograms for each month")

pool = Pool(NUM_PROCESSORS)

slicedHists = pool.map(computeMonth, monthIterator())


logMsg("Merging histograms across months")

histTuple = mergeHistogramTuples(slicedHists)
(hist_lon, hist_lat, hist_straightline, hist_time, hist_minutes, hist_dist, hist_miles, hist_winding, hist_pace) = histTuple

		


logMsg('Saving...')

try:
	os.mkdir("hist_results")
except:
	pass


hist_lon.saveToFile('hist_results/lon.csv')
hist_lat.saveToFile('hist_results/lat.csv')
hist_straightline.saveToFile('hist_results/straightline.csv')
hist_time.saveToFile('hist_results/time.csv')
hist_minutes.saveToFile('hist_results/minutes.csv')
hist_dist.saveToFile('hist_results/dist.csv')
hist_miles.saveToFile('hist_results/miles.csv')
hist_winding.saveToFile('hist_results/winding.csv')
hist_pace.saveToFile('hist_results/pace.csv')

logMsg('Done.')