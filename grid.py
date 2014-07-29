from datetime import date, datetime, timedelta
from pandas import to_datetime
from sets import Set
import csv
import os
from tools import *

weekdayname = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
COMPUTE_WINDING_FACTOR = True

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
	
class Trip:
	header_line = []
	@staticmethod
	def initHeader(header):
		#Maps header names to column index
		Trip.header_line = header
		Trip.header = {}
		for i in range(len(header)):
			Trip.header[header[i].strip()] = i
			
	def __init__(self, csvLine):
		self.csvLine = csvLine
		
		self.fromLon = float(csvLine[Trip.header["pickup_longitude"]])
		self.fromLat = float(csvLine[Trip.header["pickup_latitude"]])
		self.toLon = float(csvLine[Trip.header["dropoff_longitude"]])
		self.toLat = float(csvLine[Trip.header["dropoff_latitude"]])
		#self.time = float(csvLine[Trip.header["trip_time_in_secs"]])
		self.dist = float(csvLine[Trip.header["trip_distance"]])
		
		self.driver_id = csvLine[Trip.header["hack_license"]]
		
		#pt = datetime.strptime(csvLine[Trip.header["pickup_datetime"]], "%Y-%m-%d %H:%M:%S")
		#pt = to_datetime(csvLine[Trip.header["pickup_datetime"]])	
		pt = parseUtc(csvLine[Trip.header["pickup_datetime"]])
		self.pt = pt
		#dt = datetime.strptime(csvLine[Trip.header["dropoff_datetime"]], "%Y-%m-%d %H:%M:%S")
		#dt = to_datetime(csvLine[Trip.header["dropoff_datetime"]])
		dt = parseUtc(csvLine[Trip.header["dropoff_datetime"]])		
		duration = dt - pt
		self.time = int(duration.total_seconds())
		
		
		if(self.dist==0):
			self.pace = 0
		else:
			self.pace = float(self.time) / self.dist		
		
		self.date = pt.date()
		self.hour = pt.hour
	
		self.straight_line_dist = approxdist(self.fromLat, self.fromLon,self.toLat, self.toLon)
		
		if(self.straight_line_dist<=0):
			self.winding_factor = 1
		else:
			self.winding_factor = self.dist / self.straight_line_dist
		
		self.has_other_error=False
	
	#All of the different types of errors that could occur
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
	def isValid(self):
		#First filter obvious errors		
		
		
		if(self.pt.year==2010 and self.pt.month==8):
			return Trip.ERR_DATE
		if(self.pt.year==2010 and self.pt.month==9):
			return Trip.ERR_DATE
		
		
		if(self.toLat < 40.4 or self.fromLat < 40.4):
			return Trip.ERR_GPS
		if(self.toLat > 41.1 or self.fromLat > 41.1):
			return Trip.ERR_GPS
		if(self.toLon < -74.25 or self.fromLon < -74.25):
			return Trip.ERR_GPS
		if(self.toLon > -73.5 or self.fromLon > -73.5):
			return Trip.ERR_GPS

		if(self.straight_line_dist < .001):
			return Trip.ERR_LO_STRAIGHTLINE
		if(self.straight_line_dist > 20):
			return Trip.ERR_HI_STRAIGHTLINE
				
		if(self.dist < .001):
			return Trip.ERR_LO_DIST
		if(self.dist > 20):
			return Trip.ERR_HI_DIST
		
		if(self.winding_factor < .95):
			return Trip.ERR_LO_WIND

		if(self.time < 10):
			return Trip.ERR_LO_TIME
		if(self.time > 7200):
			return Trip.ERR_HI_TIME
		
		if(self.pace < 10):
			return Trip.ERR_LO_PACE
		if(self.pace > 7200):
			return Trip.ERR_HI_PACE
		
		
		#Next filter data that is not necessarily an error
		#But is still not useful for the analysis
		if(self.toLat < 40.6 or self.fromLat < 40.6):
			return Trip.BAD_GPS
		if(self.toLat > 40.9 or self.fromLat > 40.9):
			return Trip.BAD_GPS
		if(self.toLon < -74.05 or self.fromLon < -74.05):
			return Trip.BAD_GPS
		if(self.toLon > -73.7 or self.fromLon > -73.7):
			return Trip.BAD_GPS
			
		if(self.straight_line_dist < .001):
			return Trip.BAD_LO_STRAIGHTLINE
		if(self.straight_line_dist > 8):
			return Trip.BAD_HI_STRAIGHTLINE
				
		if(self.dist < .001):
			return Trip.BAD_LO_DIST
		if(self.dist > 15):
			return Trip.BAD_HI_DIST
		
		if(self.winding_factor < .95):
			return Trip.BAD_LO_WIND
		if(self.winding_factor > 5):
			return Trip.BAD_HI_WIND
			

		if(self.time < 60):
			return Trip.BAD_LO_TIME
		if(self.time > 3600):
			return Trip.BAD_HI_TIME
		
		if(self.pace < 40):
			return Trip.BAD_LO_PACE
		if(self.pace > 3600):
			return Trip.BAD_HI_PACE

		
		return Trip.VALID

	def __str__(self):
		
		s = "<<TRIP>>\n" + "driver " + self.driver_id + "\ntime " + str(self.time) + "\n" + "dist " + str(self.dist) + "\n"
		return s

	

class Entry:
	def __init__(self, fromCell, toCell):
		self.fromCell = fromCell
		self.toCell = toCell

		self.numtrips = 0.0		#Sum(1)
		self.s_time = 0.0			#Sum(t)
		self.ss_time = 0.0			#Sum(t^2)
		self.s_dist = 0.0			#Sum(d)
		self.ss_dist = 0.0			#Sum(d^2)
		self.ss_time_over_dist = 0.0	#Sum(t^2 / d)
		
		self.s_wind = 0
		self.ss_wind = 0
		
		
		self.drivers = Set()
		
		#self.trips = []
		
		self.error_counts = [0]*25
	
	def __str__(self):
		s = "<<ENTRY>>\n" + "time " + str(self.s_time) + "\n" + "dist " + str(self.s_dist) + "\n" + " num " + str(self.numtrips)
		return s
	
	#Records a trip by updating count, time, and distance totals
	def record(self, trip):
		self.numtrips += 1
		self.s_time += trip.time
		self.ss_time += trip.time**2
		self.s_dist += trip.dist
		self.ss_dist += trip.dist**2
		self.ss_time_over_dist += (trip.time**2 / trip.dist)
		
		self.drivers.add(trip.driver_id)
		#self.trips.append(trip)
		


			
		#if(trip.winding_factor < 1):
		#	print str(trip.winding_factor) + "=" + str(trip.dist) + "/" + str(trip.straight_line_dist) + " " + str(trip.pt) + " " + str(trip.driver_id) + " " + str(trip.fromLat) + "," + str(trip.fromLon) + " --> " + str(trip.toLat) + "," + str(trip.toLon)
	
		self.s_wind += trip.winding_factor
		self.ss_wind += trip.winding_factor**2
		
		self.error_counts[Trip.VALID] += 1
	
		

class GridSystem:
	currentDate = None
	currentHour = 0
	
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
		self.dates = []
	
	def begin(self):
		try:
			os.mkdir(self.dirName)
		except:
			pass
		
		self.countFp = open(self.dirName + "/count_features.csv", "w")
		self.countF = csv.writer(self.countFp)
		
		self.paceFp = open(self.dirName + "/pace_features.csv", "w")
		self.paceF = csv.writer(self.paceFp)
		
		self.paceVarFp = open(self.dirName + "/pace_var_features.csv", "w")
		self.paceVarF = csv.writer(self.paceVarFp)
		
		self.milesFp = open(self.dirName + "/miles_features.csv", "w")
		self.milesF = csv.writer(self.milesFp)
		
		
		self.driversFp = open(self.dirName + "/drivers_features.csv", "w")
		self.driversF =  csv.writer(self.driversFp)
		
		self.globalFp = open(self.dirName + "/global_features.csv", "w")
		self.globalF = csv.writer(self.globalFp)
		
		self.errorFp = open(self.dirName + "/errors.csv", "w")
		self.errorF = csv.writer(self.errorFp)
		
		
		for w in (self.countF, self.paceF, self.paceVarF, self.milesF, self.driversF):
			header = ["Date", "Hour", "Weekday"]
			for fromCell in self.cells:
				for toCell in self.cells:
					header.append(str(fromCell) + "-" + str(toCell))
			w.writerow(header)
		
		for w in (self.countFp, self.paceFp, self.paceVarFp, self.milesFp, self.driversFp):
			w.flush()
		

		self.globalF.writerow(["Date", "Hour", "Weekday", "Count", "Pace", "Miles", "Drivers", "AvgWind", "SdWind", 'VALID','BAD_GPS','ERR_GPS','BAD_LO_STRAIGHTLINE','BAD_HI_STRAIGHTLINE','ERR_LO_STRAIGHTLINE','ERR_HI_STRAIGHTLINE','BAD_LO_DIST','BAD_HI_DIST','ERR_LO_DIST','ERR_HI_DIST','BAD_LO_WIND','BAD_HI_WIND','ERR_LO_WIND','ERR_HI_WIND','BAD_LO_TIME','BAD_HI_TIME','ERR_LO_TIME','ERR_HI_TIME','BAD_LO_PACE','BAD_HI_PACE','ERR_LO_PACE','ERR_HI_PACE','ERR_DATE','ERR_OTHER'])
		self.globalFp.flush()		
		self.errorF.writerow(Trip.header_line + ["error_code"])		
		self.errorFp.flush()
	
	def close(self):
		self.commitEntry()
		self.countFp.close()
		self.paceFp.close()
		self.paceVarFp.close()
		self.milesFp.close()
		self.driversFp.close()
		self.globalFp.close()
		self.errorFp.close()

		
			
	def reset(self):
		self.entries = {}
		for fromCell in self.cells:
			for toCell in self.cells:
				#Create the entry and store it in the dictionary
				entry = Entry(fromCell, toCell)
				self.entries[(fromCell, toCell)] = entry
		self.globalEntry = Entry(None, None)

		
	
	#Gets the Cell which contains some geographical point
	def getCell(self, lon, lat):
		
		
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
	#This updates the count, time, and distance variables
	def record(self, trip):
		


		if(trip==None):
			self.recordError(trip)
			return

		if(trip.has_other_error):
			self.recordError(trip)
			return
			
		
		if(self.currentDate==None):
			self.currentDate = date(year=trip.date.year, month=trip.date.month, day=1)
			self.currentHour = 0
			self.reset()
				
		

		while(trip.date>self.currentDate or trip.hour>self.currentHour):
			self.commitEntry()
			self.reset()
			
			
			self.currentHour += 1
			if(self.currentHour >= 24):
				self.currentHour = 0
				self.currentDate += timedelta(days=1)
			#self.currentDate = trip.date
			#self.currentHour = trip.hour
			
			if(self.currentHour==0):
				logMsg("Advancing to " + str(self.currentDate))
		
		entry = self.getEntry(trip.fromLon, trip.fromLat, trip.toLon, trip.toLat)
		

		if(entry != None and trip.isValid()==Trip.VALID):	
			entry.record(trip)
			self.globalEntry.record(trip)
		else:
			self.recordError(trip)

	def recordError(self, trip):
		if(trip==None):
			return
		
		error_code = trip.isValid()
		if(error_code==Trip.VALID):
			error_code = Trip.ERR_OTHER
		
		self.globalEntry.error_counts[error_code] += 1
		
		#if(error_code != Trip.ERR_DATE):
		#	self.errorF.writerow(trip.csvLine + [error_code])

				
	def writeCellTable(self, dirName):
		fileName = os.path.join(dirName, "cell_dimensions.csv")
		w = csv.writer(open(fileName, "w"))
		header = ["x", "y", "lLon", "rLon", "bLat", "tLat"]
		w.writerow(header)
		for cell in self.cells:
			line = [cell.x, cell.y, cell.lLon, cell.rLon, cell.bLat, cell.tLat]
			w.writerow(line)
			
	
	def commitEntry(self):
		if(not self.currentDate is None):
			weekday = weekdayname[self.currentDate.weekday()]
			line = [str(self.currentDate), self.currentHour, weekday]
			vline = [str(self.currentDate), self.currentHour, weekday]
			
			#Write pace features
			for fromCell in self.cells:
				for toCell in self.cells:
					entry = self.entries[(fromCell, toCell)]
					if(entry.s_dist==0 or entry.numtrips < 5):
						pace = 0
						v_pace = 0
					else:
						pace = entry.s_time / entry.s_dist
						correction = entry.s_dist / (entry.s_dist**2 - entry.ss_dist)
						v_pace = correction * (entry.ss_time_over_dist - (entry.s_time**2)/entry.s_dist)

					line.append(pace)
					vline.append(v_pace)
			self.paceF.writerow(line)
			self.paceFp.flush()
			self.paceVarF.writerow(vline)
			self.paceVarFp.flush()
	
			
			line = [str(self.currentDate), self.currentHour, weekday]
			#Write count features
			for fromCell in self.cells:
				for toCell in self.cells:
					entry = self.entries[(fromCell, toCell)]
					line.append(entry.numtrips)
			self.countF.writerow(line)
			self.countFp.flush()
					
			line = [str(self.currentDate), self.currentHour, weekday]
			#Write total distance features
			for fromCell in self.cells:
				for toCell in self.cells:
					entry = self.entries[(fromCell, toCell)]
					line.append(entry.s_dist)
			self.milesF.writerow(line)
			self.milesFp.flush()
			
			line = [str(self.currentDate), self.currentHour, weekday]
			#Write driver count features
			for fromCell in self.cells:
				for toCell in self.cells:
					entry = self.entries[(fromCell, toCell)]
					line.append(len(entry.drivers))
			self.driversF.writerow(line)
			self.driversFp.flush()
			
			#Write global entry
			if(self.globalEntry.s_dist==0):
				pace = 0
				avg_wind = 0
				sdev_wind = 0
			else:
				pace = self.globalEntry.s_time / self.globalEntry.s_dist
				
			if(self.globalEntry.numtrips > 0):
				avg_wind = self.globalEntry.s_wind / self.globalEntry.numtrips
				variance = (self.globalEntry.ss_wind / self.globalEntry.numtrips) - (avg_wind)**2

				sdev_wind = math.sqrt(variance)
			else:
				avg_wind = 0
				sdev_wind = 0
			
			self.globalF.writerow([str(self.currentDate), self.currentHour, weekday, self.globalEntry.numtrips, pace, self.globalEntry.s_dist, len(self.globalEntry.drivers), avg_wind, sdev_wind] + self.globalEntry.error_counts)
			self.globalFp.flush()
		else:
			print("self.currentDate is None")
			
		
