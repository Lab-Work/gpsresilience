# -*- coding: utf-8 -*-
"""
A few utility methods used by various other files.

Created on Sat May  3 12:33:42 2014

@author: brian
"""
from datetime import datetime, timedelta
import math
import re
#import psycopg2
from numpy.linalg import norm

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


#Computes euclidean distance between two vectors
#Arguments
	#v1, v2 - Numpy matrices
def euclideanDist(v1, v2):
	return norm(v1 - v2)

	



EARTH_RADIUS = 3963.1676 #In miles
#computes distance between two lat-lon points, assuming spherical earth
#Uses the Haversine formula. See: http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
#Arguments:
	#(lat1, lon1) - a tuple representing the first coordinate
	#(lat2, lon2) - a tuple representing the second coordinate
#Returns:
	#The distance between these coordinates in miles
def haversine((lat1,lon1), (lat2,lon2)):
	[lat1, lon1, lat2, lon2] = map(math.radians, [lat1, lon1, lat2, lon2])
	lat_haversine = math.sin((lat2-lat1)/2) * math.sin((lat2-lat1)/2)
	lon_haversine = math.sin((lon2 - lon1)/2) * math.sin((lon2 - lon1)/2)
	cosine_term = math.cos(lat1) * math.cos(lat2)
	distance = 2 * EARTH_RADIUS * math.asin(math.sqrt(lat_haversine + cosine_term*lon_haversine))
	return distance

#An optimized function which approximates the haversine formula in NYC
#Assumes that the earth is flat (which is close enough for small areas)
#Arguments:
	#(lat1, lon1) - a tuple representing the first coordinate
	#(lat2, lon2) - a tuple representing the second coordinate
#Returns:
	#The approximate distance between these coordinates in miles
def approxdist_nyc((lat1,lon1), (lat2,lon2)):
	#In NYC:
	#1 degree lat ~= 69.1703234284 miles
	#1 degree lon ~= 52.3831781372 miles
	#The magic numbers are the squares of these values
	squared = (4784.533643189461*(lat1-lat2)*(lat1-lat2) + 2743.9973517536278*(lon1-lon2)*(lon1-lon2))
	
	if(squared > 0):
		return math.sqrt(squared)
	else:
		return 0
	 
#Normalizes a vector in-place
#Arguments:
	#vector - a list or Numpy vector
def normalize(vector):
	s = sum(vector)
	for i in range(len(vector)):
		vector[i] = float(vector[i]) / s
		

#A builder function - yields a squence of datetime objects
#Arguments:
	#start_date - a datetime object. the first date of the sequence
	#end_date - a datetime object. the end of the date sequence (non inclusive)
	#delta - a timedelta object.  The step size
#Yields:
	#All intermediate dates between start_date and end_date, with time intervals given by delta
def dateRange(start_date, end_date, delta=timedelta(hours=1)):
	d = start_date
	while(d < end_date):
		yield d
		d += delta

#Rounds a datetime to a given granularity (1 hour, 15 minutes, etc..)
#Arguments
	#dt - a datetime object
	#granularity - a timedelta object
#Returns:
	#a datetime, rounded to the given granularity
def roundTime(dt, granularity):
	start_time = datetime(year=2000,month=1,day=1,hour=0)	
	
	tmp = dt - start_time
	
	rounded = int(tmp.total_seconds() / granularity.total_seconds())
	
	return start_time + rounded*granularity


#Extracts column IDs from a table header
#Arguments:
	#header_row - a list of strings representing the header of a table
#Returns:
	#a dictionary which maps column names (strings) to column ID (int)
def getHeaderIds(header_row):
	mapping = {}
	for i in range(len(header_row)):
		mapping[header_row[i]] = i
	return mapping

#Returns true if all entries in a list/vector are nonzero
#Arguments:
	#v - the list or numpy vector
#Returns:
	#True if all elements of v are nonzero, False if any of them are zero
def allNonzero(v):
	for num in v:
		if(num==0):
			return False
	return True

#Returns all of the items in list l, except x
#If x appears more than once, all occurrences will be removed
#Arguments:
	#l - a list, or some other iterable object
	#x - an item that occurs in l
#Returns:
	#A new list which does not contain x
def allBut(l, x):
	newL = []
	for v in l:
		if(not (v==x).all()):
			newL.append(v)
	return newL




#An optimized datetime parser for UTC format - this is roughly 4x faster than datetime.strptime()
#Credit to Alec Mori (ajmori2@illinois.edu)
#Arguments:
	#dateStr - a string in UTC format.
#Returns:
	#A datetime object
def parseUtc(dateStr):
	return datetime(year = int(dateStr[0:4]), month = int(dateStr[5:7]), day = int(dateStr[8:10]), hour = int(dateStr[11:13]), minute = int(dateStr[14:16]), second = int(dateStr[18:]))



#Finds a quantile of a list of sorted values.  For example, the .5 quantile will return the median.
#If the quantile falls between two values, linear interpolation is used
#Arguments:
	#sortedVals - a list of numbers sorted in INCREASING order
	#quant - A number between 0 and 1
#Returns:
	#A float representing the quantile
def getQuantile(sortedVals, quant):
	#The quantile might fall between two values - this gives their indexes
	#If the quantile falls perfectly on one value, then i==j
	i = int(math.floor(len(sortedVals) * quant))
	j = int(math.ceil(len(sortedVals) * quant))
	lowV = sortedVals[i]
	hiV = sortedVals[j]
	
	val = lowV + (hiV - lowV) * (len(sortedVals)*quant - i)

	return val



def binarySearch(sortedVals, start, end, testVal):
	
	if(testVal <= sortedVals[start]):
		return start
	
	if(testVal >= sortedVals[end-1]):
		return end-1
	
	m = int((start + end)/2)
	
	if(testVal < sortedVals[m]):
		return binarySearch(sortedVals, start, m, testVal)
	else:
		return binarySearch(sortedVals, m, end, testVal)


def findQuantile(sortedVals, testVal):
	i = binarySearch(sortedVals, 0, len(sortedVals), testVal)
	
	q = (float(i) + .5)/len(sortedVals)
	return q


#Performs addition in log-space without underflow error
#Formally, returns:  log(e^v1 + e^v2 + e^v3 + ...)
#See: http://stackoverflow.com/questions/9336701/how-to-deal-with-underflow-in-scientific-computing
#Arguments:
	#vals - A list of log-values
#Returns:
	#The log-sum of values.
def addLogs(logVals):
	m = max(logVals)
	s = 0
	for v in logVals:
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


def splitList(lst, numSegments):
    for (lo, hi) in splitRange(len(lst), numSegments):
        yield lst[lo:hi]


#Returns an arbitrary element from a collection or iterable.  Generally the first one
#Arguments:
	#my_collection - some collection or iterable like a set, list, or dictionary
#Returns:
	#An arbitrary element from this collection
def arbitraryElement(my_collection):
	for e in my_collection:
		break
	return e


# An iterator which wraps a round a database cursor
# http://code.activestate.com/recipes/137270-use-generators-for-fetching-large-db-record-sets/
def resultIter(cursor, arraysize=10000):
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result

#Parses a point Well-Known-Text like POINT(-122.403099060059 37.7927589416504)
#into a tuple (lat, lon) - note that the order of coordinates is reversed
wktSplitter = re.compile('\(| |\)')
def parsePointWKT(wktString):
	toks = wktSplitter.split(wktString)
	return (float(toks[2]), float(toks[1]))


def connectToDB(confFilename):
	with open(confFilename, "r") as f:
		connString = f.read()
		conn = psycopg2.connect(connString)
		return conn
		

# A simple class which emulates the behavior of a Process Pool, but only uses
# one CPU.  Useful for 
class DefaultPool():
    def __init__(self):
        self._processes=1
        
    def map(self, fun, args):
        return map(fun, args)
    
    def close(self):
        pass
    
	