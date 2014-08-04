import csv
import os
import shutil
from datetime import datetime
from grid import *
from regions import *
from multiprocessing import Pool
import shutil


#Global settings
TMP_DIR = "working_space"			#A directory for intermediate results.  Will be deleted at the end
FINAL_OUTPUT_DIR = "4year_features"	#A directory for final results
NUM_PROCESSORS = 8				#Number of cores to employ for parallel processing

#Processes a month of trip data and outputs one month of features (mean pace vectors, trip counts, etc...) to a tmp directory
#Many of these can be run in parallel
#Arguments: Takes one tuple for ease of use with Pool.map().  The tuple contains:
	#year - an integer. the year containing the month of interest
	#month - an integer (1 through 12) the month to be processed
	#slice_id - a unique identifier for this (year,  month) pair.  Used to name the tmp files
#Returns: The name of the tmp directory created for this month
def processMonth((year, month, slice_id)):
	#The year and month give the input file
	infile = "../new_chron/FOIL" + str(year) + "/trip_data_" + str(month) + ".csv"	
	
	#The slice_id gives us the output directory - make it
	outdir = TMP_DIR + "/slice_" + str(slice_id)
	shutil.rmtree(outdir, ignore_errors=True)
	os.mkdir(outdir)
	
	#Begin the RegionSystem for this output directory - this will start outputting files there
	gridSystem = RegionSystem(outdir)
	
	logMsg('Parsing file ' + infile)
	
	#Open the input file as a CSV
	with open(infile, 'r') as filePointer:
		csvReader = csv.reader(filePointer)
		
		#Read the header and extract column ids from it
		header = csvReader.next()
		Trip.initHeader(header)
		
		#Read the rest of the file
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
	
	#Finalize the output
	gridSystem.close()

	#Return the name of the temporary directory that was created for this month	
	return outdir


#Takes all of the temporary output directories created by processMonth() and merges them into one
#(Many folders, each with 6 files) --> (one folder with 6 large files)
#Arguments:
	#slice_dirs - a list of names of temporary directories.  These names are returned by processMonth()
	#out_dir - the directory where final output will be placed
def mergeTempFiles(slice_dirs, out_dir):
	logMsg("Merging tmp files")
	shutil.rmtree(out_dir, ignore_errors=True)
	os.mkdir(out_dir)
	
	#Files that we care about (one for each type of feature):
	#count_features.csv    miles_features.csv  pace_var_features.csv
	#drivers_features.csv  global_features.csv  pace_features.csv
	feature_types = ["count", "miles", "pace_var", "drivers", "global", "pace"]
	
	#Create a file object for each feature type
	out_file_pointers = {}
	for ft in feature_types:
		fname = out_dir + "/" + ft + "_features.csv"
		out_file_pointers[ft] = open(fname, 'w')
	
	
	first_slice = True
	
	#Iterate through temporary folders
	for slice_dir in slice_dirs:
		#Iterate through the files (one for each feature type) in this folder
		for ft in feature_types:
			try:
				#Open the temporary file as input
				fname = slice_dir + "/" + ft + "_features.csv"
				infile = open(fname, 'r')
				
				
				#If this is the first file, the header should be copied to the output file
				#Otherwise, it should be skipped
				if(not first_slice):
					infile.next()

				#Copy the rest of the lines to the correct output file
				for line in infile:
					out_file_pointers[ft].write(line)
			except:
				#Ignore lines with errors
				pass

		#First slice is complete - headers should not be copied anymore
		first_slice = False
			


#An iterator function - produces tuples which serve as inputs to the processMonth() function
#(This is convenient for parallel processing)
#Each tuple represents a month to be processed (year and month), as well as a unique slice_id
def sliceIterator():
	slice_id = 0
	#Iterate through all years/months
	for year in [2010, 2011, 2012, 2013]:
		for month in range(1, 13):
			#This tuple represents the arguments to processMonth()
			yield (year, month, slice_id)
			#Increment slice_id
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
