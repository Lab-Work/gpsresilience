import math
from math import log, sqrt
import csv
import scipy.stats

def NormalLnl(mean, sdev, equalsVal):
	l = math.log(1/(sdev * math.sqrt(2*math.pi)))
	l -= ((equalsVal-mean)**2 / (2*sdev**2))
	return l


	

def LogNormalLnl(mean, sdev, equalsVal):
	try:
		z = equalsVal
		l = math.log(1) - math.log(z) - math.log(sdev) - math.log(2 * math.pi)/2
		l -= (math.log(z) - mean)**2 / (2*sdev**2)
	except:
		print mean
		print sdev
		print equalsVal
		
	return l

def KernelLnl(samp, bandwidth, equalsVal):
	
	trim = .05
	srt = sorted(samp)
	begin = int(len(srt)*trim)
	end = len(srt) - begin
	trimmed = srt[begin:end]	
	
	#print(len(samp))
	#print(begin)
	#print(end)
	#print len(trimmed)
	#print
	
	dens = 0
	for val in trimmed:
		lnl = NormalLnl(val, bandwidth, equalsVal)
		dens += math.exp(lnl) / len(srt)
		
	try:
		return math.log(dens)
	except:
		#print dens
		#print lnl
		return -10

r = csv.reader(open("features/pace_features.csv", "r"))

t = []
colids = {}
rowids = {}
header = True

s = {}
ss = {}
n = {}

s_log = {}
ss_log = {}

samp = {}

print("Reading file...")
for line in r:
	if(header):
		for j in range(len(line)):
			colids[line[j]] = j
		firstLine = line
		header = False
	else:
		for zone in colids:
			
			if(colids[zone] > 2):
				day = line[colids["Weekday"]]
				hour = int(line[colids["Hour"]])
				key = (day, hour, zone)
				if(not key in s):
					s[key] = 0
					ss[key] = 0
					s_log[key] = 0
					ss_log[key] = 0
					n[key] = 0
					samp[key] = []
				pace = float(line[colids[zone]])
				if(pace > 0.0):
					s[key] += pace
					ss[key] += pace ** 2
					
					s_log[key] += log(pace)
					ss_log[key] += log(pace) ** 2
					
					n[key] += 1
					samp[key].append(pace)
		t.append(line)

print("Fitting distributions...")
for key in samp:
	sampl = samp[key]
	s[key] = 0
	ss[key] = 0
	s_log[key] = 0
	ss_log[key] = 0
	n[key] = 0
	
	"""
	trim = .05
	srt = sorted(sampl)
	begin = int(len(srt)*trim)
	end = len(srt) - begin
	trimmed = srt[begin:end]
	"""
	trimmed = sampl
	
	for pace in trimmed:
		s[key] += pace
		ss[key] += pace ** 2
					
		s_log[key] += log(pace)
		ss_log[key] += log(pace) ** 2
					
		n[key] += 1

print("Writing output...")

w_n = csv.writer(open("distributions/normal_1tail.csv", "w"))
w_ln = csv.writer(open("distributions/lognormal.csv", "w"))
w_k = csv.writer(open("distributions/kernel.csv", "w"))

w_n.writerow(firstLine)
w_ln.writerow(firstLine)
w_k.writerow(firstLine)


n_count = 0
l_count = 0
for line in t:
	row_n = list(line)
	row_ln = list(line)
	row_k = list(line)
	
	for i in range(3, len(line)):
		
		day = line[colids["Weekday"]]
		hour = int(line[colids["Hour"]])
		zone = firstLine[i]
		key = (day, hour, zone)
		
		pace = float(line[i])
		
		if(pace>0):
			#normal lnls
			avg = s[key] / n[key]
			var = ss[key] / n[key] - avg**2
			sdev = sqrt(var)
			#print(sdev)
			norm = scipy.stats.norm(avg, sdev)
			tail = norm.cdf(pace)
			if(tail > .5):
				tail = 1 - tail
			if(tail==0):
				tail=.0000000000000000000001
			normal_lnl = log(tail)
			
			#lognormal lnl
			avg = s_log[key] / n[key]
			var = ss_log[key] / n[key] - avg**2
			sdev = sqrt(var)
			log_normal_lnl = LogNormalLnl(avg, sdev, pace)
			
			sampl = samp[key]
			k_lnl = KernelLnl(sampl, 30, pace)
			
			"""
			if(normal_lnl > log_normal_lnl):
				row[i] = "N"
				n_count += 1
			else:
				row[i] = "L"
				l_count += 1
			"""
			row_n[i] = normal_lnl
			row_ln[i] = log_normal_lnl
			row_k[i] = k_lnl
			

		
	w_n.writerow(row_n)
	w_ln.writerow(row_ln)
	w_k.writerow(row_k)

print("normal   : " + str(n_count))
print("lognormal: " + str(l_count))
	
