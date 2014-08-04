import csv
import os
import shutil
from datetime import datetime
from grid import *
from regions import *
from multiprocessing import Pool
import shutil

start_time = datetime.now()


TMP_DIR = "working_space"
FINAL_OUTPUT_DIR = "4year_features"
NUM_PROCESSORS = 8


def processMonth((year, month, slice_id)):
	infile = "../new_chron/FOIL" + str(year) + "/trip_data_" + str(month) + ".csv"	
	
	outdir = TMP_DIR + "/slice_" + str(slice_id)
	shutil.rmtree(outdir, ignore_errors=True)
	os.mkdir(outdir)
	gridSystem = RegionSystem(outdir)
	
	logMsg('Parsing file ' + infile)
	
	with open(infile, 'r') as filePointer:
		csvReader = csv.reader(filePointer)
		header = csvReader.next()
		Trip.initHeader(header)
		
		for line in csvReader:

			try:
				trip = Trip(line) #Parse the csv line into a trip object
			except ValueError:
				trip = None      #A trip of None indicates a parsing error
				
			
			#Ignore trips that are placed in the wrong month file
			if(trip!= None and (year!=trip.date.year or month!=trip.date.month)):
				trip.has_other_error = True
			
			#Record the trip - if trip==None, an error will be recorded
			gridSystem.record(trip)
	
	gridSystem.close()
	
	return outdir


def mergeTempFiles(slice_dirs, out_dir):
	logMsg("Merging tmp files")
	shutil.rmtree(out_dir, ignore_errors=True)
	os.mkdir(out_dir)
	
	#Files that we care about (one for each type of feature):
	#count_features.csv    errors.csv           miles_features.csv  pace_var_features.csv
	#drivers_features.csv  global_features.csv  pace_features.csv
	feature_types = ["count", "miles", "pace_var", "drivers", "global", "pace"]
	
	out_file_pointers = {}
	for ft in feature_types:
		fname = out_dir + "/" + ft + "_features.csv"
		out_file_pointers[ft] = open(fname, 'w')
	
	
	first_slice = True
	for slice_dir in slice_dirs:
		for ft in feature_types:
			try:
				fname = slice_dir + "/" + ft + "_features.csv"
				infile = open(fname, 'r')
				
				
				#If this is the first file, the header should be copied to the output file
				#Otherwise, it should be skipped
				if(not first_slice):
					infile.next()

				for line in infile:
					out_file_pointers[ft].write(line)
			except:
				pass

		#First slice is complete - headers should not be copied anymore
		first_slice = False
			



def sliceIterator():
	slice_id = 0
	for year in [2010, 2011, 2012, 2013]:
		for month in range(1, 13):
			#This tuple represents the arguments to processMonth()
			yield (year, month, slice_id)
			slice_id += 1
	



#########################################################################################################
################################### MAIN CODE BEGINS HERE ###############################################
#########################################################################################################
if(__name__=="__main__"):
	#Setup temporary directory to store intermediate results for each month
	logMsg("Creating working directory for temp files...")
	shutil.rmtree(TMP_DIR, ignore_errors=True)
	os.mkdir(TMP_DIR)
	
	#Run the main code on each month in parallel (to the extent possible on this machine)
	#Each month will get a subdirectory inside the temporary directory
	logMsg("Processing months in parallel (" + str(NUM_PROCESSORS) + " cores)")
	pool = Pool(NUM_PROCESSORS) #Initialize the pool
	slice_dirs = pool.map(processMonth, sliceIterator()) #Map the main function onto each month (slice) in parallel
	#slice_dirs contains all of the intermediate subdirectories.  These will be merged in the next step
	
	
	#Merge intermediate results into large files in one final output folder
	logMsg("Merging output files")
	mergeTempFiles(slice_dirs, FINAL_OUTPUT_DIR)
	
	logMsg("Cleaning up")
	shutil.rmtree(TMP_DIR, ignore_errors=True)	
	
	logMsg("Done.")	
