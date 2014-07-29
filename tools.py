# -*- coding: utf-8 -*-
"""
A few utility methods used by various other files.

Created on Sat May  3 12:33:42 2014

@author: brian
"""
from datetime import datetime
import math

program_start = datetime.now()
#A convenient print statement for long runs - also includes a timestamp at the beginning of the message
#Arguments:
	#msg - a string to be printed
def logMsg(msg):
	td = datetime.now() - program_start
	print "[" + str(td) + "]  " + str(msg)


#A print statement intended to log the percentage of completion of some task with many iterations
#Can be called many times, but only prints when the percentage is a "nice" number, rounded to a given number of digits
#Arguments
	#num - the current iteration
	#outof - the total number of iterations
	#How many digits should the percentage be rounded to?
def logPerc(num, outof, digits):
	rounded = round(float(num)/outof, digits)
	
	prev = round(float(num-1)/outof, digits)
	
	if(prev < rounded):
		logMsg(str(rounded*100) + "%")


#helper function. Computes euclidean distance between two vectors
def euclideanDist(v1, v2):
	s = 0
	for i in range(len(v1)):
		s += (v1[i] - v2[i]) **2
	return math.sqrt(s)
	

EARTH_RADIUS = 3963.1676
#computes distance between two lat-lon points, assuming spherical earth
def haversine((lat1,lon1), (lat2,lon2)):
	[lat1, lon1, lat2, lon2] = map(math.radians, [lat1, lon1, lat2, lon2])
	lat_haversine = math.sin((lat2-lat1)/2) * math.sin((lat2-lat1)/2)
	lon_haversine = math.sin((lon2 - lon1)/2) * math.sin((lon2 - lon1)/2)
	cosine_term = math.cos(lat1) * math.cos(lat2)
	distance = 2 * EARTH_RADIUS * math.asin(math.sqrt(lat_haversine + cosine_term*lon_haversine))
	return distance

def approxdist(lat1,lon1, lat2,lon2):
	#In NYC
	#1 degree lat ~= 69.1703234284
	#1 degree lon ~= 52.3831781372
	squared = (4784.533643189461*(lat1-lat2)*(lat1-lat2) + 2743.9973517536278*(lon1-lon2)*(lon1-lon2))
	
	if(squared > 0):
		return math.sqrt(squared)
	else:
		return 0
	 
#helper function. Normalizes a vector in-place
def normalize(vector):
	s = sum(vector)
	for i in range(len(vector)):
		vector[i] = float(vector[i]) / s
		

#A builder function - yields a squence of datetime objects
#Arguments:
	#start_date - a datetime object. the first date of the sequence
	#end_date - a datetime object. the end of the date sequence (non inclusive)
	#delta - a timedelta object.  The step size
def dateRange(start_date, end_date, delta):
	d = start_date
	while(d < end_date):
		yield d
		d += delta

#Rounds a datetime to a given granularity (1 hour, 15 minutes, etc..)
#Arguments
	#dt - a datetime object
	#granularity - a timedelta object
#Returns a datetime, rounded to the given granularity
def roundTime(dt, granularity):
	start_time = datetime(year=2000,month=1,day=1,hour=0)	
	
	tmp = dt - start_time
	
	rounded = int(tmp.total_seconds() / granularity.total_seconds())
	
	return start_time + rounded*granularity


#Takes a list, which represents the header row of a table
#Returns a dictionary which maps the string column names to integer column ids
def getHeaderIds(header_row):
	mapping = {}
	for i in range(len(header_row)):
		mapping[header_row[i]] = i
	return mapping

#Returns true if all entries in a list/vector are nonzero
def allNonzero(v):
	for num in v:
		if(num==0):
			return False
	return True

#Returns all of the items in list l, except x
#If x appears more than once, all occurrences will be removed
#Params:
	#l - a list, or some other iterable object
	#x - an item that occurs in l
	#returns - a new smaller list which does not contain x
def allBut(l, x):
	newL = []
	for v in l:
		if(not (v==x).all()):
			newL.append(v)
	return newL




#An optimized datetime parser for UTC format
#Credit to Alec Mori
def parseUtc(DateTime):
	return datetime(year = int(DateTime[0:4]), month = int(DateTime[5:7]), day = int(DateTime[8:10]), hour = int(DateTime[11:13]), minute = int(DateTime[14:16]), second = int(DateTime[18:]))


#A builder function - yields a squence of datetime objects
#Arguments:
	#start_date - a datetime object. the first date of the sequence
	#end_date - a datetime object. the end of the date sequence (non inclusive)
	#delta - a timedelta object.  The step size
def dateRange(start_date, end_date, delta):
	d = start_date
	while(d < end_date):
		yield d
		d += delta

#Rounds a datetime to a given granularity (1 hour, 15 minutes, etc..)
#Arguments
	#dt - a datetime object
	#granularity - a timedelta object
#Returns a datetime, rounded to the given granularity
def roundTime(dt, granularity):
	start_time = datetime(year=2000,month=1,day=1,hour=0)	
	
	tmp = dt - start_time
	
	rounded = int(tmp.total_seconds() / granularity.total_seconds())
	
	return start_time + rounded*granularity


#Takes a list, which represents the header row of a table
#Returns a dictionary which maps the string column names to integer column ids
def getHeaderIds(header_row):
	mapping = {}
	for i in range(len(header_row)):
		mapping[header_row[i]] = i
	return mapping


def getQuantile(sortedVals, quant):
	i = int(math.floor(len(sortedVals) * quant))
	j = int(math.ceil(len(sortedVals) * quant))
	lowV = sortedVals[i]
	hiV = sortedVals[j]
	
	val = lowV + (hiV - lowV) * (len(sortedVals)*quant - i)

	
	return val

def addLogs(vals):
	m = max(vals)
	s = 0
	for v in vals:
		s += math.exp(v - m)
	return math.log(s) + m
	

#Splits a range of numbers into segments - useful for splitting data for parallel processing
#Size - the number of elements to be split
#numSegments - the number of segments to split them into
def splitRange(size, numSegments):
	for i in range(numSegments):
		lo = int(size * float(i)/numSegments)
		hi = int(size * float(i+1)/numSegments)
		yield (lo,hi)