# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 14:00:47 2014

@author: Brian Donovan (briandonovan100@gmail.com)

Much credit goes to:
"""

from Crypto.Cipher import AES
import os
import csv
import shutil
from multiprocessing import Pool


from tools import *
BLOCK_SIZE=32
NUM_PROCESSORS = 8


#Use a cipher to encrypt a hex string as another hex string
def code(orig, cipher):
	b64 = orig.decode('hex')
	b64Enc = cipher.encrypt(b64)
	return b64Enc.encode('hex').upper()

	

#Encrypt all medallions and hack_licenses in the file
def processMonth((year, month, secret)):
	tripInFile = "../new_chron/FOIL" + str(year) + "/trip_data_" + str(month) + ".csv"
	tripOutFile = "../anon/FOIL" + str(year) + "/trip_data_" + str(month) + ".csv"
	fareInFile = "../new_chron/FOIL" + str(year) + "/trip_fare_" + str(month) + ".csv"
	fareOutFile = "../anon/FOIL" + str(year) + "/trip_fare_" + str(month) + ".csv"
	
	tripInFp = open(tripInFile, "r")
	tripOutFp = open(tripOutFile, "w")
	fareInFp = open(fareInFile, "r")
	fareOutFp = open(fareOutFile, "w")
	
	tripInCsv = csv.reader(tripInFp)
	tripOutCsv = csv.writer(tripOutFp)
	fareInCsv = csv.reader(fareInFp)
	fareOutCsv = csv.writer(fareOutFp)
	
	
	
	
	logMsg("Processing " + str(year) + "-" + str(month))
	cipher = AES.new(secret)

	
	#Write the header
	tripOutCsv.writerow(tripInCsv.next())
	fareOutCsv.writerow(fareInCsv.next())
	badmonth = 0
	try:	
		while(True):
			tripLine = tripInCsv.next()
			fareLine = fareInCsv.next()
			try:
				dt = parseUtc(tripLine[5])
				if(dt.year==year and dt.month==month):
					tripLine[0] = code(tripLine[0], cipher)
					tripLine[1] = code(tripLine[1], cipher)
					fareLine[0] = code(fareLine[0], cipher)
					fareLine[1] = code(fareLine[1], cipher)
					
					if(tripLine[0]==fareLine[0] and tripLine[1] == fareLine[1]):
						tripOutCsv.writerow(tripLine)
						fareOutCsv.writerow(fareLine)
					else:
						logMsg("MISMATCH ERROR")
						logMsg("-- " + str(tripLine))
						logMsg("-- " + str(fareLine))
				else:
					badmonth += 1
			except:
				logMsg("Parse error on " + str(tripLine))
	except StopIteration:
		logMsg("Done with " + str(year) + "-" + str(month))
		
	
	tripInFp.close()
	tripOutFp.close()
	fareInFp.close()
	fareOutFp.close()
	return tripInFile + "  :  " + str(badmonth)
	


def monthIterator():
	#generate secrets
	secrets = {}
	for y in range(2010, 2014):
		secrets[y] = os.urandom(BLOCK_SIZE)
	
	
	for y in range(2010, 2014):
		for m in range(1, 13):
			yield (y, m, secrets[y])



shutil.rmtree("../anon", ignore_errors=True)
os.mkdir("../anon")
os.mkdir("../anon/FOIL2010")
os.mkdir("../anon/FOIL2011")
os.mkdir("../anon/FOIL2012")
os.mkdir("../anon/FOIL2013")

pool = Pool(NUM_PROCESSORS)
output = pool.map(processMonth, monthIterator())


for line in output:
	print line