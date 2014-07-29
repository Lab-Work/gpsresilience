import csv
import datetime
import math
from math import log, sqrt
import scipy.stats


def NormalLnl(mean, sdev, equalsVal):
	#l = math.log(1/(sdev * math.sqrt(2*math.pi)))
	#l -= ((equalsVal-mean)**2 / (2*sdev**2))

	norm = scipy.stats.norm(mean, sdev)
	tail = norm.cdf(equalsVal)
	#tail = norm.pdf(equalsVal) * sdev	
	if(tail > .5):
		tail = 1 - tail
	if(tail==0):
		tail=.0000000000000000000001
	return log(tail)	


def LogNormalLnl(mean, sdev, equalsVal):
	try:
		z = equalsVal
		l = math.log(1) - math.log(z) - math.log(sdev) - math.log(2 * math.pi)/2
		l -= (math.log(z) - mean)**2 / (2*sdev**2)
	except:
		print mean
		print sdev
		print equalsVal
		return 0
		
	return l


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


def quantile(sortedVals, testVal):
	i = binarySearch(sortedVals, 0, len(sortedVals), testVal)
	
	q = (float(i) + .5)/len(sortedVals)
	return q

def oneTail(sortedVals, testVal):
	q = quantile(sortedVals, testVal)
	if(q < .5):
		return q
	else:
		return (1-q)
		
		
def getQuantile(sortedVals, quant):
	i = int(math.floor(len(sortedVals) * quant))
	j = int(math.ceil(len(sortedVals) * quant))
	lowV = sortedVals[i]
	hiV = sortedVals[j]
	
	val = lowV + (hiV - lowV) * (len(sortedVals)*quant - i)

	
	return val

def trapezoidArea(y_vals, x_width):
	s = 0
	s += float(y_vals[0]) / 2
	s += float(y_vals[-1]) / 2
	s += float(sum(y_vals[1:-1]))
	
	return s * x_width

def rectArea(y_vals, x_width):
	return sum(y_vals) * x_width

def posAndNegativeArea(y_vals1, y_vals2, x_width):
	s_pos = 0
	s_neg = 0
	for i in range(len(y_vals1)):
		#print str(y_vals1[i]) + "\t" + str(y_vals2[i])
		if(y_vals1[i] > y_vals2[i]):
			s_pos += (y_vals1[i] - y_vals2[i])
		else:
			s_neg += (y_vals2[i] - y_vals1[i])

	#print (s_pos, s_neg)

	return (s_pos, s_neg)

def ksmooth(timeseries, bandwidth):
	smoothed = list(timeseries)
	n = scipy.stats.norm(0,bandwidth)
	
	for i in range(len(timeseries)):
		begin = max(0,i-bandwidth*2)
		end = min(len(timeseries),i+bandwidth*2)
		
		weighted_sum = 0
		weight = 0
		
		for j in range(begin,end):
			w = n.pdf(j-i)
			try:
				weighted_sum += w*timeseries[j]
			except:
				print timeseries[j]
			weight += w
		smoothed[i] = weighted_sum / weight
	return smoothed

r = csv.reader(open("4year_features/pace_features.csv", "r"))

t = []
colids = {}
rowids = {}
header = True


samp = {}

print("Reading file...")
for line in r:
	t.append(line)
	if(header):
		for j in range(len(line)):
			colids[line[j]] = j
		header = False
	else:
		for zone in colids:
			
			if(colids[zone] > 2):
				day = line[colids["Weekday"]]
				hour = int(line[colids["Hour"]])
				key = (day, hour, zone)
				if(not key in samp):
					samp[key] = []
				pace = float(line[colids[zone]])
				if(pace > 0.0):
					samp[key].append(pace)

print("Fitting distributions...")
s = {}
ss = {}
s_log = {}
ss_log = {}
maxval = {}
minval = {}
n_distrib = {}
n = {}
for key in samp:
	samp[key] = sorted(samp[key])
	
	srt = samp[key]
	s[key] = 0
	ss[key] = 0
	s_log[key] = 0
	ss_log[key] = 0
	n[key] = 0
	
	"""
	trim = .15
	begin = int(len(srt)*trim)
	end = len(srt) - begin
	trimmed = srt[begin:end]		
	"""
	
	trimmed = srt
	for pace in trimmed:
		s[key] += pace
		ss[key] += pace ** 2
					
		s_log[key] += log(pace)
		ss_log[key] += log(pace) ** 2
					
		n[key] += 1
	
	
print("Calculating lnl")			

#28th - 10th

lnlT = []
lnlHeader = ["date", "hour", "lnl_norm", "lnl_emp", "lnl_lognorm", "lnl_smooth", "lnl_lognorm_smooth"]

lnlColIds = {}
for i in range(len(lnlHeader)):
	lnlColIds[lnlHeader[i]] = i
	
zscore_w = csv.writer(open("results/zscore.csv","w"))

header = True
for line in t:
	line_out = line[0:3]
	if(header):
		header = False
		zscore_w.writerow(line)
	else:
		
		lnl_norm = 0
		lnl_emp = 0
		lnl_lognorm = 0
		
		total_zones = 0
		zones_with_data = 0
		for zone in colids:
			date = line[colids["Date"]]
			day = line[colids["Weekday"]]
			hour = int(line[colids["Hour"]])
			
			if(colids[zone] > 2):
				val = float(line[colids[zone]])
				key = (day, hour, zone)
				
				avg = s[key] / n[key]
				var = ss[key] / n[key] - avg**2
				sdev = math.sqrt(var)
				
				
				l_avg = s_log[key] / n[key]
				l_var = ss_log[key] / n[key] - l_avg**2
				l_sdev = math.sqrt(l_var)
				
				
				sample = samp[key]
				
				#account for missing data
				#Assume that the pace is just the average value - this is a conservative estimate if we are proving that a day is unusual
				if(val == 0):
					#val = avg
					print("missing val - " + str(date) + " " + str(hour) + ":00")
					#print(str(NormalLnl(avg, sdev, val)))
					#print
					zscore = 0
				else:
					lnl_norm += NormalLnl(avg, sdev, val)
					
					zscore = (val - avg)/sdev					
					
					lnl_emp += math.log(oneTail(sample, val))
					lnl_lognorm += LogNormalLnl(l_avg, l_sdev, val)
					zones_with_data += 1
				
				line_out.append(zscore)
				total_zones += 1
			
			#print(float(total_zones)/zones_with_data)
		if(zones_with_data==0):
			lnl_norm = 0
			lnl_lognorm = 0
			lnl_emp = 0
		elif(not total_zones == zones_with_data):
			print lnl_norm
			lnl_norm *= (float(total_zones)/zones_with_data)
			print lnl_norm
			print
			lnl_emp *= (float(total_zones)/zones_with_data)
			lnl_lognorm *= (float(total_zones)/zones_with_data)
		
		zscore_w.writerow(line_out)
		
		row = [date, hour, lnl_norm, lnl_emp, lnl_lognorm, 0, 0]
		lnlT.append(row)

print("computing quality")

#calculate quality metric (pace_min / pace_obs) for each day
#as well as average pace for every (weekday, hour) pair - this allows us to get the quality of an average week
r = csv.reader(open("4year_features/global_features.csv", "r"))
pace_header = {}
pace_s = {}
pace_n = {}
pace_min = None
firstLine = True
paceT = []
for line in r:
	if(firstLine):
		for i in range(len(line)):
			pace_header[line[i]] = i
		firstLine = False
	else:
		paceT.append(line)
		key = (line[pace_header["Weekday"]], line[pace_header["Hour"]])
		if(key not in pace_s):
			pace_s[key] = 0
			pace_n[key] = 0
		pace = float(line[pace_header["Pace"]])
		pace_s[key] += pace
		pace_n[key] += 1
		if(pace > 0 and (pace_min==None or pace < pace_min)):
			pace_min = pace

qualityTable = []
qualityHeaderRow = ["Date", "Hour", "PaceObs", "PaceAvg", "PaceMin", "QObs", "QAvg"]
qualityHeader = {}
for i in range(len(qualityHeaderRow)):
	qualityHeader[qualityHeaderRow[i]] = i 
w = csv.writer(open("results/quality_1tail.csv", "w"))
w.writerow(qualityHeaderRow)
for line in paceT:
	newLine = [line[pace_header["Date"]], line[pace_header["Hour"]]]
	
	pace_obs = float(line[pace_header["Pace"]])
	key = (line[pace_header["Weekday"]], line[pace_header["Hour"]])
	pace_avg = (pace_s[key] / pace_n[key])
	if(pace_obs>0):
		q_obs = pace_min / pace_obs
	else:
		q_obs = 0
		
	q_avg = pace_min / pace_avg

	newLine += [pace_obs, pace_avg, pace_min, q_obs, q_avg]
	qualityTable.append(newLine)
	w.writerow(newLine)
	



print("smoothing")

lnlList = []
for line in lnlT:
	lnlList.append(line[lnlColIds["lnl_norm"]])

LNL_THRESHOLD = getQuantile(sorted(lnlList), .2)
print "Threshold = " + str(LNL_THRESHOLD)

eventTable = []
eventTable.append(["StartDate", "StartHour", "EndDate", "EndHour", "Duration", "Impact", "PosImpact", "NegImpact", "AvgQuality"])
prev_date = None
prev_hour = None
prev_i = None
SMOOTHING_HOURS = 5

smoothed =  ksmooth(lnlList, SMOOTHING_HOURS)


for i in range(len(lnlT)):
	start = max(0, i-SMOOTHING_HOURS)
	end = min(len(lnlT), i + SMOOTHING_HOURS)
	#print str(i) + " : " + str(start) + " -> " + str(end)
	
	#get smoothed value from normal lnl
	samp = []
	for j in range(start, end):
		samp.append(lnlT[j][lnlColIds["lnl_norm"]])
	samp.sort()
	median = getQuantile(samp, .5)
	lnlT[i][lnlColIds["lnl_smooth"]] = smoothed[i]
	
	#get smoothed value from normal lnl
	samp = []
	for j in range(start, end):
		samp.append(lnlT[j][lnlColIds["lnl_lognorm"]])
	samp.sort()
	median2 = getQuantile(samp, .5)
	lnlT[i][lnlColIds["lnl_lognorm_smooth"]] = median2
	
	if(lnlT[i][lnlColIds["lnl_smooth"]] < LNL_THRESHOLD and prev_date==None):
		prev_date = lnlT[i][lnlColIds["date"]]
		prev_hour = lnlT[i][lnlColIds["hour"]]
		prev_i = i
	elif(lnlT[i][lnlColIds["lnl_smooth"]] > LNL_THRESHOLD and not prev_date==None):
		current_date = lnlT[i][lnlColIds["date"]]
		current_hour = lnlT[i][lnlColIds["hour"]]
		duration = i - prev_i
		
		#get impact by comparing this event's quality to that of a standard week
		q_obs = []
		q_avg = []
		for line in qualityTable[prev_i: i]:
			q_obs.append(line[qualityHeader["QObs"]])
			q_avg.append(line[qualityHeader["QAvg"]])
		
		#obs_impact = trapezoidArea(q_obs, 1)
		#expt_impact = trapezoidArea(q_avg, 1)
		
		#impact = obs_impact - expt_impact
		
		obs_impact = rectArea(q_obs, 1)
		(pos_impact, neg_impact) = posAndNegativeArea(q_obs, q_avg, 1)
		impact = pos_impact - neg_impact
		
		
		avg_quality = obs_impact / duration
		
		
		
		eventTable.append([prev_date, prev_hour, current_date, current_hour, duration, impact, pos_impact, neg_impact, avg_quality])
		prev_date = None
		prev_hour = None

print("outputting")

w = csv.writer(open("results/lnl_over_time_1tail.csv", "w"))
w.writerow(lnlHeader)
w.writerows(lnlT)

w = csv.writer(open("results/detected_events_1tail.csv", "w"))
w.writerows(eventTable)



