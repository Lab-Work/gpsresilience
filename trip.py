# -*- coding: utf-8 -*-
"""
Contains the Trip class, which represents a single taxi trip.

Created on Wed Aug  6 14:17:57 2014

@author: Brian Donovan (briandonovan100@gmail.com)
"""
from tools import *

#A single taxi trip - contains information such as coordinates, times, etc...
#Can be parsed from a line of a CSV file via the constructor
#Some trips contain obvious errors - the isValid() method reveals this
class Trip:
	header_line = []

	#A static method which enables the __init__() method to work properly
	#Given the header line from a CSV file, it determines the index of each column (by name)
	@staticmethod
	def initHeader(header):
		Trip.header_line = header
		Trip.header = {} #Maps header names to column index
		for i in range(len(header)):
			Trip.header[header[i].strip()] = i
	
	#Constructs a Trip object using a line from a CSV file.  Assumes that Trip.initHeader() has already been called
	#Arguments:
		#csvLine - A list, which has been parsed from a CSV data file
	def __init__(self, csvLine):
		#Store the actual data in case we need it later...
		self.csvLine = csvLine
		
		#Parse coordinates from the cssv data
		self.fromLon = float(csvLine[Trip.header["pickup_longitude"]])
		self.fromLat = float(csvLine[Trip.header["pickup_latitude"]])
		self.toLon = float(csvLine[Trip.header["dropoff_longitude"]])
		self.toLat = float(csvLine[Trip.header["dropoff_latitude"]])
		self.dist = float(csvLine[Trip.header["trip_distance"]])
		
		self.driver_id = csvLine[Trip.header["hack_license"]]
		
		
		#Parse the pickup datetime the fast way (defined in tools.csv) The slow way is commented out for reference
		#pt = datetime.strptime(csvLine[Trip.header["pickup_datetime"]], "%Y-%m-%d %H:%M:%S")
		self.pickup_time = parseUtc(csvLine[Trip.header["pickup_datetime"]]) #A datetime object

		#Dropoff times... same deal as pickup times
		#dt = datetime.strptime(csvLine[Trip.header["dropoff_datetime"]], "%Y-%m-%d %H:%M:%S")
		dropoff_time = parseUtc(csvLine[Trip.header["dropoff_datetime"]])		
		
		duration = dropoff_time - self.pickup_time  #Dropoff time is used to compute duration (timedelta object)
		self.time = int(duration.total_seconds()) #Time stores the duration as seconds
		
		#Compute pace (if possible)
		if(self.dist==0):
			self.pace = 0
		else:
			self.pace = float(self.time) / self.dist		
		
	
		#Straightline distance between pickup and dropoff coordinates		
		self.straight_line_dist = approxdist_nyc((self.fromLat, self.fromLon),(self.toLat, self.toLon))
		
		#Winding factor = ratio of true distance over straightline distance (typically something like 1.5)
		if(self.straight_line_dist<=0):
			self.winding_factor = 1
		else:
			self.winding_factor = self.dist / self.straight_line_dist
		
		self.has_other_error=False
	
	#All of the different types of errors that could occur - most are based on thresholds
	#An ERROR trip is one that is clearly impossible (e.g. a winding factor of .5, which violates Euclidean geometry)
	#A BAD trip is one that is technically possible, but not useful for our analysis (e.g. a 10-second trip)
	VALID = 0
	BAD_GPS = 1
	ERR_GPS = 2
	BAD_LO_STRAIGHTLINE=3
	BAD_HI_STRAIGHTLINE=4
	ERR_LO_STRAIGHTLINE=5
	ERR_HI_STRAIGHTLINE=6
	BAD_LO_DIST=7
	BAD_HI_DIST=8
	ERR_LO_DIST=8
	ERR_HI_DIST=10	
	BAD_LO_WIND=11
	BAD_HI_WIND=12
	ERR_LO_WIND=13
	ERR_HI_WIND=14	
	BAD_LO_TIME=15
	BAD_HI_TIME=16
	ERR_LO_TIME=17
	ERR_HI_TIME=18	
	BAD_LO_PACE=19
	BAD_HI_PACE=20
	ERR_LO_PACE=21
	ERR_HI_PACE=22
	ERR_DATE = 23
	ERR_OTHER = 24
	
	#This method implements data filtering
	#Tells whether the trip is valid, by applying various thresholds to the features.
	#Returns: An integer error code.  0 means it is a valid trip, 1-24 are different types of errors, listed above
	def isValid(self):
		#These two months contain a very high number of errors, so they cannot be trusted
		if(self.pickup_time.year==2010 and self.pickup_time.month==8):
			return Trip.ERR_DATE
		if(self.pickup_time.year==2010 and self.pickup_time.month==9):
			return Trip.ERR_DATE
		
		
		#First filter obvious errors
		
		#GPS coordinates (in degrees) not reasonable
		if(self.toLat < 40.4 or self.fromLat < 40.4):
			return Trip.ERR_GPS
		if(self.toLat > 41.1 or self.fromLat > 41.1):
			return Trip.ERR_GPS
		if(self.toLon < -74.25 or self.fromLon < -74.25):
			return Trip.ERR_GPS
		if(self.toLon > -73.5 or self.fromLon > -73.5):
			return Trip.ERR_GPS

		#Distance between start and end coordinates (in miles) not reasonable
		if(self.straight_line_dist < .001):
			return Trip.ERR_LO_STRAIGHTLINE
		if(self.straight_line_dist > 20):
			return Trip.ERR_HI_STRAIGHTLINE
				
		#Metered distance (in miles) not reasonable
		if(self.dist < .001):
			return Trip.ERR_LO_DIST
		if(self.dist > 20):
			return Trip.ERR_HI_DIST
		
		#In euclidean space, the winding factor (metered dist / straightline dist) must be >= 1
		#We allow some small room for rounding errors and GPS noise
		if(self.winding_factor < .95):
			return Trip.ERR_LO_WIND

		#Unreasonable trip time (in seconds)
		if(self.time < 10):
			return Trip.ERR_LO_TIME
		if(self.time > 7200):
			return Trip.ERR_HI_TIME
		
		#Unreasonable pace (in second/mile)
		if(self.pace < 10):
			return Trip.ERR_LO_PACE
		if(self.pace > 7200):
			return Trip.ERR_HI_PACE
		
		
		#Next filter data that is not necessarily an error
		#But is still not useful for the analysis
		
		#Restrict analysis to Manhattan and a small surrounding area
		if(self.toLat < 40.6 or self.fromLat < 40.6):
			return Trip.BAD_GPS
		if(self.toLat > 40.9 or self.fromLat > 40.9):
			return Trip.BAD_GPS
		if(self.toLon < -74.05 or self.fromLon < -74.05):
			return Trip.BAD_GPS
		if(self.toLon > -73.7 or self.fromLon > -73.7):
			return Trip.BAD_GPS
		
		#Really long trips (in miles) are not representative
		if(self.straight_line_dist > 8):
			return Trip.BAD_HI_STRAIGHTLINE
				
		if(self.dist > 15):
			return Trip.BAD_HI_DIST
		
		#A high winding factor indicates that the taxi did not proceed directly to its destination
		#So it is not representative of its start and end regions
		if(self.winding_factor > 5):
			return Trip.BAD_HI_WIND
			
		#Really short or really long trips are not representative
		if(self.time < 60):
			return Trip.BAD_LO_TIME
		if(self.time > 3600):
			return Trip.BAD_HI_TIME
		
		#These speeds are technically possible, but not indicative of overall traffic
		if(self.pace < 40):
			return Trip.BAD_LO_PACE
		if(self.pace > 3600):
			return Trip.BAD_HI_PACE

		
		return Trip.VALID

	#For debugging
	def __str__(self):
		
		s = "<<TRIP>>\n" + "driver " + self.driver_id + "\ntime " + str(self.time) + "\n" + "dist " + str(self.dist) + "\n"
		return s
