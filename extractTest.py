import csv
import os
import shutil
from datetime import datetime
from grid import *
#from cluster import *
from regions import *


start_time = datetime.now()

print("Allocating...")

#grid2
#gridSystem = GridSystem(-74.04, -73.775, 5, 40.63, 40.835, 5)
#gridname = "grid2"

#grid3
#gridSystem = GridSystem(-74.02, -73.938, 4, 40.7, 40.815, 6)
#gridname = "grid3"

#cluster1
#gridSystem = ClusterSystem("cluster1/clusters.csv")
#gridname = "cluster1"

gridSystem = RegionSystem("4year_features_z")
gridname = "region1"


invalids = 0
for y in ["FOIL2012"]:
	for n in range(8,11):
		filename = "../../new_chron/" + y + "/trip_data_" + str(n) + ".csv"
		print("Reading file " + filename)
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
					if(y=="FOIL" + str(trip.date.year) and trip.isValid()==Trip.VALID):
						gridSystem.record(trip)
					else:
						gridSystem.recordError(trip)
				except ValueError as e:
					print e.message
					gridSystem.recordError(trip)
					invalids += 1
			i += 1
			if(i%1000000==0):
				print("Read " + str(i) + " rows")
				
gridSystem.close()

end_time =  datetime.now()
program_duration = end_time - start_time

print("Processing took " + str(program_duration))
