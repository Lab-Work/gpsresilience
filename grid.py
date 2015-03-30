"""
Contains methods for sequentially computing features of trips between various regions within a city over time.
The implementation in this class is a simple grid of regions, but this behavior can easily
be overridden in child classes (such as regions.py)

Created on Sat May  3 12:33:42 2014

@author: Brian Donovan (briandonovan100@gmail.com)
"""

from datetime import date, datetime, timedelta
from sets import Set
import csv
import os

from tools import *
from trip import *

weekdayname = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

#We need at least this many trips to accurately estimate the average pace
MIN_SAMPLE_SIZE = 5



#Abstractly represents one region of the city
class Cell:
	x = 0
	y = 0
	
	lLon = 0.0
	rLon = 0.0
	
	bLat = 0.0
	tLat = 0.0
	def __str__(self):
		return "(" + str(self.x) + " " + str(self.y) + ")"
	def gridRange(self):
		return "lon(" + str(self.lLon) + " --> " + str(self.rLon) + ")  lat(" + str(self.bLat) + " --> " + str(self.tLat) + ")"
	
#This class represents the unit of analysis - an origin destination pair at a point in time
#Specifically, it is identified by a pair of Cells
#We will, for example, be computing the average pace of trips between region A and region B at time T
class Entry:
	#Simple constructor
	#Arguments:
		#fromCell - the beginning region of trips
		#toCell - the end region of trips
	def __init__(self, fromCell, toCell):
		#Store the cells
		self.fromCell = fromCell
		self.toCell = toCell

		#Initialize all features to zero - they will be incremented when trips are matched to this entry
		self.numtrips = 0.0			#Sum(1)
		self.s_time = 0.0			#Sum(t)
		self.ss_time = 0.0			#Sum(t^2)
		self.s_dist = 0.0			#Sum(d)
		self.ss_dist = 0.0			#Sum(d^2)
		self.ss_time_over_dist = 0.0	#Sum(t^2 / d)
		
		self.s_wind = 0
		self.ss_wind = 0
		
		
		self.drivers = Set()			#The set of unique drivers
		
		#self.trips = []
		
		self.error_counts = [0]*25		#A list which counts various types of errors.  The indexes are founded in trip.py right above the definition of isValid()
	
	def __str__(self):
		s = "<<ENTRY>>\n" + "time " + str(self.s_time) + "\n" + "dist " + str(self.s_dist) + "\n" + " num " + str(self.numtrips)
		return s
	
	#Records a trip into this entry by updating the features
	#Arguments:
		#trip - the Trip to be recorded
	def record(self, trip):
		self.numtrips += 1
		self.s_time += trip.time
		self.ss_time += trip.time**2
		self.s_dist += trip.dist
		self.ss_dist += trip.dist**2
		self.ss_time_over_dist += (trip.time**2 / trip.dist)
		
		self.drivers.add(trip.driver_id)
		#self.trips.append(trip)
		

	
		self.s_wind += trip.winding_factor
		self.ss_wind += trip.winding_factor**2
		
		self.error_counts[Trip.VALID] += 1
	
#The time granularity of analysis - this timedelta object will be used a lot, so let's just generate it once...	
HOUR_GRANULARITY = timedelta(hours = 1)

#This object is used to sequentially process trips in chronological order
#It contains a number of Cells (or regions), as well as Entries (pairs of cells)
#It has the ability to record a trip, which updates the relevant entry
#It can also output the current entries, and reset the current entries so the next hour can be processed
#This behavior is fully encapsulated - THE ONLY METHOD THAT NEES TO BE CALLED FROM OUTSIDE OF THE CLASS IS record().
#All files will be written automatically
class GridSystem:
	currentTime = None #Stores the internal time state of this GridSystem	
	#This is the hour that we are currently processing trips for - it is advanced when necessary
	
	#A simple way of initializing a grid system, by dividing the map into an NxM grid
	#Arguments:
		#lLon - the leftmost longitude of the grid
		#rLon - the rightmost longitude of the grid
		#nLon - the number of ways to split the grid horizontally. The width of each cell will be (rLon - lLon)/nLon
		#bLat - the bottom latitude of the grid
		#tLat - the top latitude of the grid
		#nLat - the number of ways to split the grid vertically. The height of each cell will be (tLat - bLat)/nLat
	def __init__(self, lLon, rLon, nLon, bLat, tLat, nLat):
		#Determine width and height of cells
		width = (rLon - lLon)/nLon
		height = (tLat - bLat)/nLat
		
		self.cells = []
		#Create all possible cells in the grid system
		for x in range(nLon):
			for y in range(nLat):
				cell = Cell()
				#Cell number
				cell.x = x
				cell.y = y
				#Corresponding lat-lon
				cell.lLon = lLon + x*width
				cell.rLon = lLon + (x+1)*width
				cell.bLat = bLat + y*height
				cell.tLat = bLat + (y+1)*height
				#add to list of cells
				self.cells.append(cell)
		self.entries = {}
		
		self.dirName="4year_cells"
		self.begin()
	
	#Initialize the GridSystem for outputting features.  Opens a file for each type of feature.
	#This method should be called before record()
	def begin(self):
		try:
			os.mkdir(self.dirName)
		except:
			pass
		
		#Open the files and give them each a CSV writer object
		self.countFp = open(self.dirName + "/count_features.csv", "w")		#Trip counts from region A to region B
		self.countF = csv.writer(self.countFp)
		
		self.paceFp = open(self.dirName + "/pace_features.csv", "w")		#Average pace of trips from A to B
		self.paceF = csv.writer(self.paceFp)
		
		self.paceVarFp = open(self.dirName + "/pace_var_features.csv", "w")	#Variance of pace of trips from A to B
		self.paceVarF = csv.writer(self.paceVarFp)
		
		self.milesFp = open(self.dirName + "/miles_features.csv", "w")		#Total miles driven in trips from A to B
		self.milesF = csv.writer(self.milesFp)
		
		
		self.driversFp = open(self.dirName + "/drivers_features.csv", "w")	#Unique number of drivers seen driving from A to B
		self.driversF =  csv.writer(self.driversFp)
		
		self.globalFp = open(self.dirName + "/global_features.csv", "w")	#A special file to contain global features (across all regions)
		self.globalF = csv.writer(self.globalFp)
		
		self.errorFp = open(self.dirName + "/errors.csv", "w")			#A special file to contain error data
		self.errorF = csv.writer(self.errorFp)
		
		
		#Write a header to each file, which contains time information and the names of region pairs
		for w in (self.countF, self.paceF, self.paceVarF, self.milesF, self.driversF):
			header = ["Date", "Hour", "Weekday"]
			for fromCell in self.cells:
				for toCell in self.cells:
					header.append(str(fromCell) + "-" + str(toCell))
			w.writerow(header)
		
		#Flush files
		for w in (self.countFp, self.paceFp, self.paceVarFp, self.milesFp, self.driversFp):
			w.flush()
		
		#The global feature file gets a special header
		self.globalF.writerow(["Date", "Hour", "Weekday", "Count", "Pace", "Miles", "Drivers", "AvgWind", "SdWind", 'VALID','BAD_GPS','ERR_GPS','BAD_LO_STRAIGHTLINE','BAD_HI_STRAIGHTLINE','ERR_LO_STRAIGHTLINE','ERR_HI_STRAIGHTLINE','BAD_LO_DIST','BAD_HI_DIST','ERR_LO_DIST','ERR_HI_DIST','BAD_LO_WIND','BAD_HI_WIND','ERR_LO_WIND','ERR_HI_WIND','BAD_LO_TIME','BAD_HI_TIME','ERR_LO_TIME','ERR_HI_TIME','BAD_LO_PACE','BAD_HI_PACE','ERR_LO_PACE','ERR_HI_PACE','ERR_DATE','ERR_OTHER'])
		self.globalFp.flush()		
		self.errorF.writerow(Trip.header_line + ["error_code"])		
		self.errorFp.flush()
	
	#Finalizes results and closes all of the files being written by this GridSystem
	#This method should be called at the very end
	def close(self):
		#Commit the last entry if necessary
		self.commitEntry()
		
		#Close all of the files
		self.countFp.close()
		self.paceFp.close()
		self.paceVarFp.close()
		self.milesFp.close()
		self.driversFp.close()
		self.globalFp.close()
		self.errorFp.close()

		
	#Reset all entries to zero - should be called at the end of an hour before the next hour is processed
	def reset(self):
		#Create an Entry for every pair of regions
		self.entries = {}
		for fromCell in self.cells:
			for toCell in self.cells:
				#Create the entry and store it in the dictionary
				entry = Entry(fromCell, toCell)
				self.entries[(fromCell, toCell)] = entry
				
		#Create a special Entry for global features
		self.globalEntry = Entry(None, None)

		
	
	#Gets the Cell which contains some geographical point
	#This method should be overridden if other types of regions are desired
	def getCell(self, lon, lat):
		
		#Easy way to determine cell...
		for cell in self.cells:
			if(lon > cell.lLon and lon < cell.rLon and lat > cell.bLat and lat < cell.tLat):
				return cell
		#Return none if this point is out of bounds
		
		return None
				
	#Gets the Entry which corresponds to a given trip at a given time
	def getEntry(self, lon1, lat1, lon2, lat2):
		fromCell = self.getCell(lon1, lat1)
		toCell = self.getCell(lon2, lat2)
		#If either coordinate is invalid, return none
		if(fromCell is None or toCell is None):
			return None
		else:
			#Now that we know the cells, just combine them with the date and time
			#Then look up in hte dictionary
			return self.entries[(fromCell, toCell)]
	
	#Records a trip by finding the corresponding entry, and recording this trip within
	#This updates the features in that entry (increase count of trips, total distance, etc...)
	#TRIPS SHOULD ALWAYS BE GIVEN TO THIS METHOD IN CHRONOLOGICAL ORDER
	#When we get to the end of an hour, this method will also output the features for that hour
	#And reset all of the entries so the next hour can be computed.
	#This process is hidden from the outside - just give it a set of trips in chronological order.
	#Arguments:
		#trip - a Trip object.  This trip's pickup_time should be greater than the pickup_time of the last trip passed to this method.
	def record(self, trip):
		
		#If the trip contains an error, call recordError() instead
		if(trip==None or trip.has_other_error):
			if(self.globalEntry != None):
				self.recordError(trip)
			return

			
		
		if(self.currentTime==None):
			#This is the first trip that we have seen
			#Start time at the beginning of that trip's month
			self.currentTime = datetime(year=trip.pickup_time.year, month=trip.pickup_time.month, day=1)
			self.reset()
				
		
		
		trip_hour = roundTime(trip.pickup_time, HOUR_GRANULARITY)
		
		#If the trip's time is less than the current Time, then trips were received out of order.  Print error message.
		if(trip_hour < self.currentTime):
			logMsg("ERROR: Bad trip order -- please give trips to GridSystem in chronological order.")
			logMsg("Trip time : " + str(trip.pickup_time) + "   GridSystem current time : " + str(self.currentTime))
		
		#The trips are received in chronological order
		#Thus, if the trip occurs in the NEXT hour (or later) then THIS hour is complete.  It can be output
		#And the internal state of the GridSystem is advanced forward in time
		while(trip_hour > self.currentTime):
			self.commitEntry() #Output the set of features for the current hour
			self.reset()		#Reset the features so the next hour can be computed
			
			
			#Advance time by one hour
			self.currentTime += HOUR_GRANULARITY

			
			if(self.currentTime.hour==0):
				logMsg("Advancing to " + str(self.currentTime))
		
		#Figure out which entry this trip is assigned to, based on origin-destination coordinates
		entry = self.getEntry(trip.fromLon, trip.fromLat, trip.toLon, trip.toLat)
		
		#Update that entry's features using this trip's data
		if(entry != None and trip.isValid()==Trip.VALID):	
			entry.record(trip)
			self.globalEntry.record(trip)
		else:
			self.recordError(trip)

	#A separate method for recording trips that have an error.  Updates error counts in the global entry
	def recordError(self, trip):
		if(trip==None):
			return
		
		error_code = trip.isValid()
		if(error_code==Trip.VALID):
			error_code = Trip.ERR_OTHER
		
		self.globalEntry.error_counts[error_code] += 1
		
		#Activate the code below, if you want to build a file containing the actual error data
		
		#if(error_code != Trip.ERR_DATE):
		#	self.errorF.writerow(trip.csvLine + [error_code])

				
	
	#Writes the features from all entries into the currently open files (see begin()).
	#Should be called at the END of an hour, before reset() is called.
	def commitEntry(self):
		
		#Ignore the end of the 0th hour, where no data has been recorded yet...
		if(not self.currentTime is None):
			
			weekday = weekdayname[self.currentTime.weekday()]
			
						
			#Write pace features, and pace variance features - this is one value for each entry (pair of regions)
			line = [str(self.currentTime.date()), self.currentTime.hour, weekday]
			vline = [str(self.currentTime.date()), self.currentTime.hour, weekday]
			for fromCell in self.cells:
				for toCell in self.cells:
					entry = self.entries[(fromCell, toCell)]
					if(entry.s_dist==0 or entry.numtrips < MIN_SAMPLE_SIZE):
						#Bad sample size, output 0 as placeholder
						pace = 0
						v_pace = 0
					else:
						#Distance-weighted average pace
						pace = entry.s_time / entry.s_dist
						#Distance-weighted pace unbiased sample variance
						correction = entry.s_dist / (entry.s_dist**2 - entry.ss_dist)
						v_pace = correction * (entry.ss_time_over_dist - (entry.s_time**2)/entry.s_dist)

					line.append(pace)
					vline.append(v_pace)
			self.paceF.writerow(line)
			self.paceFp.flush()
			self.paceVarF.writerow(vline)
			self.paceVarFp.flush()
	
			#Write count features - one value for each entry (pair of regions)
			line = [str(self.currentTime.date()), self.currentTime.hour, weekday]
			for fromCell in self.cells:
				for toCell in self.cells:
					entry = self.entries[(fromCell, toCell)]
					line.append(entry.numtrips)
			self.countF.writerow(line)
			self.countFp.flush()
					
			#Write "total miles" features - one value for each entry (pair of regions)
			line = [str(self.currentTime.date()), self.currentTime.hour, weekday]
			for fromCell in self.cells:
				for toCell in self.cells:
					entry = self.entries[(fromCell, toCell)]
					line.append(entry.s_dist)
			self.milesF.writerow(line)
			self.milesFp.flush()
			
			
			#Write unique driver count features - one value for each entry (pair of regions)
			line = [str(self.currentTime.date()), self.currentTime.hour, weekday]
			for fromCell in self.cells:
				for toCell in self.cells:
					entry = self.entries[(fromCell, toCell)]
					line.append(len(entry.drivers))
			self.driversF.writerow(line)
			self.driversFp.flush()
			
			#Write global entry - this contains the same features as above, except for all trips
			if(self.globalEntry.s_dist==0):
				pace = 0
				avg_wind = 0
				sdev_wind = 0
			else:
				pace = self.globalEntry.s_time / self.globalEntry.s_dist
			
			#Compute winding vactor if possible
			if(self.globalEntry.numtrips > 0):
				avg_wind = self.globalEntry.s_wind / self.globalEntry.numtrips
				variance = (self.globalEntry.ss_wind / self.globalEntry.numtrips) - (avg_wind)**2

				sdev_wind = math.sqrt(variance)
			else:
				avg_wind = 0
				sdev_wind = 0
			
			self.globalF.writerow([str(self.currentTime.date()), self.currentTime.hour, weekday, self.globalEntry.numtrips, pace, self.globalEntry.s_dist, len(self.globalEntry.drivers), avg_wind, sdev_wind] + self.globalEntry.error_counts)
			self.globalFp.flush()
		else:
			print("self.currentTime is None")
			
		
