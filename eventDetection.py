# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 15:30:51 2014

@author: brian
"""
from tools import *
from likelihood_test import *
from datetime import datetime, timedelta
from Queue import PriorityQueue
from math import sqrt

class TimeSegment:
	def __init__(self, start_id, end_id, state):
		self.start_id= start_id
		self.end_id = end_id
		self.state = state
		self.prev = None
		self.next = None

	@staticmethod
	def buildList(lnp_list, threshold):
		
			
		
		return firstSegment
	
	def __str__(self):
		return str(self.start_id) + "," + str(self.end_id) + " : " + str(self.state)
	
	def __cmp__(self, other):
		
		if(other==None):
			return 1
		
		if(self.duration() > other.duration()):
			return 1
		elif(self.duration() < other.duration()):
			return -1
		
		if(self.state < other.state):
			return 1
		elif(self.state > other.state):
			return -1
		
		return 0

	def duration(self):
		return self.end_id - self.start_id + 1
	
	def mergeWithNeighbors(self):
		#Build the new segment.  there are 3 cases
		if(self.prev==None):
			#This is the first segment - merge with the next segment
			newSegment = TimeSegment(self.start_id, self.next.end_id, self.next.state)
		elif(self.next==None):
			#This is the last segment - merge with the previous segment
			newSegment = TimeSegment(self.prev.start_id, self.end_id, self.prev.state)
		else:
			#General case - merge with the previous AND next segments
			newSegment = TimeSegment(self.prev.start_id, self.next.end_id, self.prev.state)
		
		#Update the links to and from the previous item		
		if(self.prev!=None):			
			if(self.prev.prev !=None):
				self.prev.prev.next = newSegment
			newSegment.prev = self.prev.prev
			#del(self.prev)
		
		#Update the links to and form the next item
		if(self.next!=None):
			if(self.next.next != None):
				self.next.next.prev = newSegment
			newSegment.next = self.next.next
			#del(self.next)
		
		#del(self)
		return newSegment
	
	

class TimeSegmentList:
	def __init__(self, lnp_list, threshold):
		current_state = (lnp_list[0] > threshold)
		prevSegment = None
		self.head = None
		self.iter_segment = None
		self.lookup_table = {}
		
		for i in range(len(lnp_list)):
			aboveThreshold = lnp_list[i] > threshold
			if(aboveThreshold != current_state):

				if(prevSegment==None):
					start_id = 0
				else:
					start_id = prevSegment.end_id + 1
				
				segment = TimeSegment(start_id, i-1, current_state)
				if(prevSegment != None):
					prevSegment.next = segment
				segment.prev = prevSegment
				current_state = aboveThreshold
				prevSegment = segment
				
				if(self.head == None):
					self.head = segment
				
				self.lookup_table[(start_id, i-1)] = segment
		if(prevSegment==None):
			start_id = 0
		else:
			start_id = prevSegment.end_id + 1
		segment = TimeSegment(start_id, i, current_state)
		segment.prev = prevSegment
		if(prevSegment != None):
			prevSegment.next = segment
		if(self.head == None):
			self.head = segment
		self.lookup_table[(start_id, i)] = segment
	
	def __iter__(self):
		self.iter_segment = self.head
		return self
	
	def next(self):
		if(self.iter_segment==None):
			raise StopIteration
		else:
			tmp = self.iter_segment
			self.iter_segment = self.iter_segment.next
			return tmp
			
	def __str__(self):
		output = ""
		for segment in self:
			if(self.sorted_dates == None):
				output += str(segment) + '\n'
			else:
				output += str(segment) + " " + str(self.sorted_dates[segment.start_id]) + " " + str(self.sorted_dates[segment.end_id]) + '\n'
		return output
	
	def mergeSegment(self, segment):
		del self.lookup_table[segment.start_id, segment.end_id]
		if(segment.prev!=None):
			del self.lookup_table[segment.prev.start_id, segment.prev.end_id]
		if(segment.next!=None):
			del self.lookup_table[segment.next.start_id, segment.next.end_id]
		
		new_seg = segment.mergeWithNeighbors()
		self.lookup_table[new_seg.start_id, new_seg.end_id] = new_seg
		if(new_seg.prev==None):
			self.head = new_seg
		return new_seg
		
	def removeSmallSegmentsWithState(self, threshold, state):
		current_segment = self.head
		while(current_segment != None):
			if(current_segment.state==state and current_segment.duration() < threshold):
				current_segment = self.mergeSegment(current_segment)
			else:
				current_segment = current_segment.next
	
	def removeSmallSegmentsInOrder(self, threshold):
		pq = PriorityQueue()
		for segment in self:
			if(segment.duration() < threshold):
				pq.put(segment)
		
		while(not pq.empty()):
			segment = pq.get()
			if((segment.start_id, segment.end_id) in self.lookup_table):
				new_seg = self.mergeSegment(segment)
				if(new_seg.duration() < threshold):
					pq.put(segment)


WEEKDAY_STRINGS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
def keyFromDatetime(d):
	date_string = str(d).split()[0]
	hour = d.hour
	weekday = WEEKDAY_STRINGS[d.weekday()]
	return (date_string, hour, weekday)
	


TRIP_NAMES = []
for orig in ['E','U','M','L']:
	for dest in ['E','U','M','L']:
		TRIP_NAMES.append(orig + "->" + dest)
		
def computeEventProperties(start_key, end_key, global_pace_timeseries, expected_pace_timeseries, zscore_timeseries):
	(date, hour, weekday) = start_key
	start_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(hours = int(hour))
	
	(date, hour, weekday) = end_key
	end_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(hours = int(hour))

	duration = int((end_date - start_date + timedelta(hours=1)).total_seconds() / 3600)

	max_pace_dev = 0
	min_pace_dev = 0
	
	
	worst_zscore = float('-inf')
	worst_zscore_id = 0
	for d in dateRange(start_date, end_date + timedelta(hours=1), timedelta(hours=1)):
		key = keyFromDatetime(d)
		pace_dev = (global_pace_timeseries[key] - expected_pace_timeseries[key]) / 60.0 #Divide by 60 - convert minutes to seconds
		max_pace_dev = max(max_pace_dev, pace_dev)
		min_pace_dev = min(min_pace_dev, pace_dev)
		
		std_pace_vector = zscore_timeseries[key]
		for i in range(len(std_pace_vector)):
			if(std_pace_vector[i] > worst_zscore):
				worst_zscore = std_pace_vector[i]
				worst_zscore_id = i
			
	return [start_date, end_date, duration, max_pace_dev, min_pace_dev, TRIP_NAMES[worst_zscore_id]]
	
	
	
def getExpectedPace(global_pace_timeseries):
	grouped_sum = defaultdict(float)
	grouped_ss = defaultdict(float)	
	grouped_count = defaultdict(float)
	for (date, hour, weekday) in global_pace_timeseries:
		grouped_sum[weekday, hour] += global_pace_timeseries[date,hour,weekday]
		grouped_ss[weekday, hour] += global_pace_timeseries[date,hour,weekday] ** 2
		
		grouped_count[weekday, hour] += 1
	
	expected_pace_timeseries = {}
	sd_pace_timeseries = {}
	for (date, hour, weekday) in global_pace_timeseries:
		updated_sum = grouped_sum[weekday, hour] - global_pace_timeseries[date, hour, weekday]
		updated_ss = grouped_ss[weekday, hour] - global_pace_timeseries[date, hour, weekday] ** 2
		updated_count = grouped_count[weekday, hour] - 1
		expected_pace_timeseries[date, hour, weekday] = updated_sum / updated_count
		sd_pace_timeseries[date, hour, weekday] = sqrt((updated_ss / updated_count) - expected_pace_timeseries[date, hour, weekday] ** 2)
		
	return (expected_pace_timeseries, sd_pace_timeseries)
		





def saveEvents(timeSegments, zscore_timeseries, global_pace_timeseries, out_file):
	eventList = []	
	(expected_pace_timeseries, sd_pace_timeseries) = getExpectedPace(global_pace_timeseries)	
	
	for segment in timeSegments:
		if(segment.state==False):
			start_key = timeSegments.sorted_dates[segment.start_id]
			end_key = timeSegments.sorted_dates[segment.end_id]	

			event = computeEventProperties(start_key, end_key, global_pace_timeseries, expected_pace_timeseries, zscore_timeseries)
			eventList.append(event)
	
	eventList.sort(key = lambda x: x[2], reverse=True)
	
	w = csv.writer(open(out_file, "w"))
	w.writerow(["start_date", "end_date", "duration", "max_pace_dev", "min_pace_dev", "worst_trip"])
	for event in eventList:
		[start_date, end_date, duration, max_pace_dev, min_pace_dev, worst_trip] = event
		formattedEvent = [start_date, end_date, duration, "%.2f" % max_pace_dev, "%.2f" % min_pace_dev, worst_trip]
		w.writerow(formattedEvent)
	



def detectEventsSwitching(lnp_timeseries, zscore_timeseries, global_pace_timeseries, min_event_length, min_event_spacing, threshold_quant, out_file):
	sorted_dates = sorted(lnp_timeseries)
	lnp_list = []
	for d in sorted_dates:
		lnp_list.append(lnp_timeseries[d])
	
	threshold = getQuantile(sorted(lnp_list), threshold_quant)
	
	print threshold
	timeSegments = TimeSegmentList(lnp_list, threshold)
	timeSegments.sorted_dates = sorted_dates
	#print str(timeSegments)
	
	#timeSegments.removeSmallSegments(min_event_spacing, True)
	
	#print "***************************************************"
	#print str(timeSegments)
	#timeSegments.removeSmallSegments(min_event_length, False)

	#print "***************************************************"
	#print str(timeSegments)


	#timeSegments.removeSmallSegmentsInOrder(min_event_spacing)
	saveEvents(timeSegments, zscore_timeseries, global_pace_timeseries, "results/events_stage1.csv")
	timeSegments.removeSmallSegmentsWithState(min_event_spacing, True)
	saveEvents(timeSegments, zscore_timeseries, global_pace_timeseries, "results/events_stage2.csv")
	timeSegments.removeSmallSegmentsWithState(min_event_spacing, False)
	saveEvents(timeSegments, zscore_timeseries, global_pace_timeseries, "results/events_stage3.csv")
	

	



def readLnpTimeseries(filename):
	r = csv.reader(open(filename, "r"))
	r.next()
	timeseries = {}
	for (date,hour,weekday,full_lnl,ind_lnl,param_lnl,global_pace, expected_pace, sd_pace) in r:
		hour = int(hour)
		timeseries[(date,hour,weekday)] = float(full_lnl)
	return timeseries

def readZScoresTimeseries(filename):
	r = csv.reader(open(filename, "r"))
	r.next()
	timeseries = {}
	for line in r:
		(date, hour, weekday) = line[0:3]
		hour = int(hour)
		timeseries[(date,hour,weekday)] = map(float, line[3:])
	return timeseries

if(__name__=="__main__"):
	if(True):
		lnp_timeseries = readLnpTimeseries("results/lnl_over_time_leave1.csv")
		#(pace_timeseries, var_timeseries, count_timeseries, pace_grouped) = readPaceData("4year_features")
		global_pace_timeseries = readGlobalPace("4year_features")
		zscore_timeseries = readZScoresTimeseries('results/std_pace_vector.csv')
		
		#logMsg("Detecting events at 99% bound")
		#detectEventsSwitching(lnp_timeseries, pace_timeseries, global_pace_timeseries, 10, 10, .01, out_file="results/detected_events_99.csv")
		logMsg("Detecting events at 95% bound")
		detectEventsSwitching(lnp_timeseries, zscore_timeseries, global_pace_timeseries, 6, 6, .05, out_file="results/detected_events_95.csv")
		logMsg("Done.")
	else:
		
		ts = [0,0,0,0,1,1,0,0,0,0,1,0,1,0,1,1,1,1,0,0,0,]
