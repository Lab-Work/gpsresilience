import csv
import os
import shutil
from datetime import datetime
from grid import *
#from cluster import *
from regions import *
from multiprocessing import Process
from time import sleep
import shutil

start_time = datetime.now()




class ParseFileProcess(Process):
	def __init__(self, infile, tmp_dir, slice_id):
		super(ParseFileProcess, self).__init__()
		filename = tmp_dir + "/slice_" + str(slice_id)
		shutil.rmtree(filename, ignore_errors=True)
		os.mkdir(filename)
		self.gridSystem = RegionSystem(filename)
		self.infile = infile
		
	
	def run(self):
		logMsg('Parsing file ' + self.infile)
		r = csv.reader(open(self.infile, 'r'))		
		i = 0
		header = True
		for line in r:
			if(header):
				Trip.initHeader(line)
				header = False
			else:
				trip = None
				try:
					trip = Trip(line)
				except ValueError:
					pass
				
				
				if(trip!= None and (self.y!="FOIL" + str(trip.date.year) or self.n!= trip.date.month)):
					trip.has_other_error = True
				
				self.gridSystem.record(trip)

		self.gridSystem.close()


def mergeTempFiles(tmp_dir, out_dir):
	logMsg("Merging tmp files")
	shutil.rmtree(out_dir, ignore_errors=True)
	os.mkdir(out_dir)
	#count_features.csv    errors.csv           miles_features.csv  pace_var_features.csv
	#drivers_features.csv  global_features.csv  pace_features.csv
	feature_types = ["count", "miles", "pace_var", "drivers", "global", "pace"]
	
	out_file_pointers = {}
	for ft in feature_types:
		fname = out_dir + "/" + ft + "_features.csv"
		out_file_pointers[ft] = open(fname, 'w')
		
	for slice_id in range(48):
		for ft in feature_types:
			try:
				fname = tmp_dir + "/slice_" + str(slice_id) + "/" + ft + "_features.csv"
				infile = open(fname, 'r')
				
				if(slice_id!=0):
					infile.next()
				for line in infile:
					out_file_pointers[ft].write(line)
			except:
				pass
			


#grid2
#gridSystem = GridSystem(-74.04, -73.775, 5, 40.63, 40.835, 5)
#gridname = "grid2"

#grid3
#gridSystem = GridSystem(-74.02, -73.938, 4, 40.7, 40.815, 6)
#gridname = "grid3"

#cluster1
#gridSystem = ClusterSystem("cluster1/clusters.csv")
#gridname = "cluster1"


tmp_dir = "working_space3"
shutil.rmtree(tmp_dir, ignore_errors=True)
os.mkdir(tmp_dir)

invalids = 0

NUM_PC = 8

workers = [None] * NUM_PC


slice_id = 0
for y in ["FOIL2010", "FOIL2011", "FOIL2012", "FOIL2013"]:
	for n in range(1,13):
		filename = "../../new_chron/" + y + "/trip_data_" + str(n) + ".csv"		
		
		created_job = False
		#Polling - see if any workers are ready to accept a new job
		while(not created_job):
			for i in range(NUM_PC):
				if(workers[i]==None or not workers[i].is_alive()):
					workers[i] = ParseFileProcess(filename, tmp_dir, slice_id)
					workers[i].y = y
					workers[i].n = n
					workers[i].start()
					created_job = True
					break
				
			#Sleep for 1 second so the polling doesn't hog a CPU
			if(not created_job):
				sleep(1)
		
		slice_id += 1
		

logMsg("Joining last workers.")
for w in workers:
	if(w!=None and w.is_alive()):
		w.join()

logMsg("Merging output files")
mergeTempFiles(tmp_dir, "4year_featuresz")
	
logMsg("Done.")	

"""
filename = "../../new_chron/" + "FOIL2010" + "/trip_data_" + str(1) + ".csv"
w = ParseFileProcess(filename, tmp_dir, 0)
w.y = "FOIL2010"
w.n = 1
w.start()


w.join()
"""