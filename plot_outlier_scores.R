#Brian Donovan (briandonovan100@gmail.com)
#Plots the time-series probability computed in likelihood_test_parallel.py
#Also plots the global pace for references
#It is possible to add the detected events from eventDetection.py




#Removes the year from date strings
#For example "2012-08-15" --> "08-15"
#Arguments:
	#dates - a vector of date strings
#Returns
	#a vector of shortened date strings
shortenDates = function(dates){
	mydates = dates
	  mydates = strptime(mydates, '%Y-%m-%d')
	  mydates = format(mydates, '%m-%d')
	  return(mydates)
}



#Adds events as translucent squares on top of the probability plot
#Arguments:
	#s - a subset (by row) of the original data, representing the desired time range
	#filename - the file to read the events from
addEvents = function(s, filename){

	#Define date range of this plot
	s_dates = strptime(as.character(s$date), "%Y-%m-%d") + s$hour*3600
	MIN_DATE = min(s_dates)
	MAX_DATE = max(s_dates)

	#read events from file
	events = read.csv(filename)
	events$start_date = strptime(as.character(events$start_date), "%Y-%m-%d %H:%M:%s_")
	events$end_date = strptime(as.character(events$end_date), "%Y-%m-%d %H:%M:%s_")


	#Compute the x values by subtracting the date from the beginning of this time window
	start_x = difftime(events$start_date, MIN_DATE, units="hours")
	end_x = difftime(events$end_date, MIN_DATE, units="hours")


	#print(cbind(start_x,end_x))
	#Get the y-limits, using a quantile of the y-values (the probabilities)
	ylm = quantile(s$mahal, c(.002,1))
	
	#Draw a rectangle for each of the events
	for (i in 1:length(start_x)){
		if(end_x[i] > 0 && start_x[i] < 3*7*24){
			polygon(x=c(start_x[i], end_x[i], end_x[i], start_x[i]), y=c(ylm[1], ylm[1], ylm[2], ylm[2]), col=rgb(.5,.5,.5,.4))
		}
	}
	


}


#Adds a plot containing global pace information
#Arguments:
	#s - a subset (by row) of the original data, representing the desired time range
addPacePlot = function(s){


	#Create empty plot
	plot(0,0, type="n", main="Pace Comparison", xaxt="n", xlab="", ylab="Pace (min/mi)", xlim=c(1,nrow(s)), ylim=c(2,9), lwd=2)

  
  
  	#Draw a shaded area representing +- 1 standard deviation from the mean of expected pace
	#polygon(x=c(1:nrow(s), rev(1:nrow(s))), y = c(s$expected_pace/60 - s$sd_pace/60, rev(s$expected_pace/60 + s$sd_pace/60)), col=rgb(.5,.5,.8), border=NA)
	#Draw lines on top of this shaded area
	#lines(s$expected_pace/60 - s$sd_pace/60, col=rgb(.4,.4,.4), lwd=2)
	#lines(s$expected_pace/60 + s$sd_pace/60, col=rgb(.4,.4,.4), lwd=2)
  
  
	#Shade the area between the "observed pace" and "expected pace" curves
	#Green where the observed pace is lower, red where it is higher
	#This area is composed of many trapezoids
	for(i in 1:(nrow(s)-1)){
		if(s$global_pace[i] < s$expected_pace[i]){
			mycol = "green"
		}
		else{
			mycol = "red"
		}	  	
	  polygon(x=c(i, i+1, i+1, i), y=c(s$expected_pace[i]/60, s$expected_pace[i+1]/60, s$global_pace[i+1]/60, s$global_pace[i]/60), col=mycol, border=mycol)
	}


	#Draw lines on top
 	lines(s$global_pace/60, col="black", lwd=3)
 	lines(s$expected_pace/60, col="blue", lwd=3)
  
  

  
  
	#Create axis label from selected dates (midnight of each day)
	ids = (0:20) * 24 + 1
	short_dates = shortenDates(s$date)
	axis(1, at=ids, labels=short_dates[ids], cex.axis=.75)
  

	#Draw a vertical line on each Sunday at midnight
	abline(v=ids)
	ids2 = (0:3)*24*7 + 1
	abline(v=ids2, lwd=3)



	#Add the legend
	legend("topright", legend=c("ObsPace", "AvgPace", "1 StDev"), col=c("black", "blue", rgb(.4,.4,.4)), lwd=2, lty=1, bg="white")

}


#Adds the time-series plot of outlier scores
#Arguments:
	#s - the subset of the table for the relevant time range
	#t - the original full table
	#title - the main title for the plot
	#type - either "full" corresponding to full gaussian likelihood, or "kern" corresponding to kernel density estimate
addOutlierPlot = function(s1, t1, s2, t2, title, type="mahal"){


	#Depending on the type of outlier score, extract the right column
	if(type=="mahal"){
		s1_lnl = s1$mahal
		t1_lnl = t1$mahal
		s2_lnl = s2$mahal
		t2_lnl = t2$mahal
	}
	else if(type=="lof"){
		s1_lnl = s1$lof20
		t1_lnl = t1$lof20
		s2_lnl = s2$lof20
		t2_lnl = t2$lof20
	}
	
	#Create the plot of the outlier scores
	#plot(s1_lnl, col="black", type="l", main=title, ylim = quantile(s1_lnl, c(.002,1)), xaxt="n", xlab="", ylab="Mahalanobis Distance", lwd=1)
	plot(s1_lnl, col="black", type="l", main=title, ylim = c(0,8), xaxt="n", xlab="", ylab="Mahalanobis Distance", lwd=1)
	lines(s2_lnl, col="blue", type="l", lwd=1)

	#Use a 5% quantile on the values from the ORIGINAL data to determine the threshold
	#Draw a horizontal line for the threshold
	#abline(h=quantile(t1_lnl, c(.90, .95, .99)), col="black", lty=2)
	#abline(h=quantile(t2_lnl, c(.90,.95, .99)), col="blue", lty=2)
	  

	#Add dates as x-axis labels
	ids = (0:20) * 24 + 1
	short_dates = shortenDates(s1$date)
	axis(1, at=ids, labels=short_dates[ids], cex.axis=.75)
	  
	  
	#Draw thin lines to divide days, and thick lines to divide weeks  
	abline(v=ids)
	ids2 = (0:3)*24*7 + 1
	abline(v=ids2, lwd=3)

	#Add the legend
	#legend("topright", legend=c("M(t)", "Threshold"), col=c("black", "red"),
	#	  lwd=c(2,2), bg="white")

	legend("topright", legend=c("Coarse", "Fine"), col=c("black", "blue"), lwd=2, bg="white")
}










#Makes the standard plot, which contains probability and pace graphs
#Arguments:
	#startDate - the beginning of the desired time range to plot
	#endDate - the end of the desired time ragne to plot
	#inFile - the file that contains the time-series probabilities (see likelihood_test_parallel.py)
	#outFile - the PDF file to generate
	#title - the main title of the figure
makeplot = function(startDate, endDate, inFile, outFile, title){

	#Read table from file and select the desired subset
	t1 = read.csv("results/outlier_scores.csv")
	t1$date = as.character(t1$date)
	t1$mahal = t1$mahal / 4.0
	s1 = t1[t1$date>=startDate & t1$date<=endDate,]


	t2 = read.csv("results/link_20_normalize_outlier_scores.csv")
	t2$date = as.character(t2$date)
	s2 = t2[t2$date>=startDate & t2$date<=endDate,]



	#Create PDF  file
	print(paste("Creating", outFile))
	if(outFile!='[IGNORE]'){
		pdf(outFile, 12, 8)
	}
	par(mfrow=c(2,1), mar=c(3,5,2,1))

  

	#Add the probability plot	
	addOutlierPlot(s1, t1, s2, t2, title)
 
	#Add the pace plot
	addPacePlot(s1)

	if(outFile!='[IGNORE]'){
  		dev.off()
	}
}



makeLofPlot = function(startDate, endDate, inFile, outFile, title){
	#Read table from file and select the desired subset
	t = read.csv(inFile)
	t$date = as.character(t$date)
	s = t[t$date>=startDate & t$date<=endDate,]


	#Create PDF  
	print(paste("Creating", outFile))
	pdf(outFile, 12, 8)
	par(mfrow=c(2,1), mar=c(3,5,2,1))

	#Create the plot of the probability
	plot(s$lof1, col="black", type="l", main=title, ylim = quantile(s$lof1, c(.002,1)), xaxt="n", xlab="", ylab="Local Outlier Factor", lwd=2)
	lines(s$lof3, col="darkblue", lwd=2)
	lines(s$lof5, col="blue", lwd=2)
	lines(s$lof10, col="darkgreen", lwd=2)
	lines(s$lof20, col="green", lwd=2)
	lines(s$lof30, col="orange", lwd=2)
	lines(s$lof50, col="red", lwd=2)
	
	legend("topright",
		legend=c("k=1", "k=3", "k=5", "k=10", "k=20", "k=30", "k=50"),
		col=c("black", "darkblue", "blue", "darkgreen", "green", "orange", "red"), lwd=2)
	
	#Add dates as x-axis labels
	ids = (0:20) * 24 + 1
	short_dates = shortenDates(s$date)
	axis(1, at=ids, labels=short_dates[ids], cex.axis=.75)
	  
	  
	#Draw thin lines to divide days, and thick lines to divide weeks  
	abline(v=ids)
	ids2 = (0:3)*24*7 + 1
	abline(v=ids2, lwd=3)

	addPacePlot(s)


}


#Makes a plot that compares the gaussian density with the kernel density
#Arguments:
	#startDate - the beginning of the desired time range to plot
	#endDate - the end of the desired time ragne to plot
	#inFile - the file that contains the time-series probabilities (see likelihood_test_parallel.py)
	#outFile - the PDF file to generate
	#title - the main title of the figure
makeKernPlot = function(startDate, endDate, inFile, outFile, title){


	#Set up the PDF  
	print(paste("Creating", outFile))
	pdf(outFile, 12, 8)
	#Each page contains 2 plots
	par(mfrow=c(2,1), mar=c(3,5,2,1))

	#Read the data from file
	t = read.csv(inFile)
	t$date = as.character(t$date)
	s = t[t$date>=startDate & t$date<=endDate,]

	#Add the time-series plot of the full outulier scores
	addOutlierPlot(s, t, title, type="full")
 
	#Add the time-serires pace plot
	addPacePlot(s)
  
	#Add the time-series plot of the kernel density estimates
	addOutlierPlot(s, t, title, type="kern")
 
	#Add another pace plot
	addPacePlot(s)
	
	
	
	dev.off()
	
}


#Makes a plot to demonstrate the thrashing of the time-series probability over the thresholds
#Shows the raw events, where the probability is below the threshold
#And the filtered events, which have been corrected for thrashing
#Arguments:
	#startDate - the beginning of the desired time range to plot
	#endDate - the end of the desired time ragne to plot
	#inFile - the file that contains the time-series probabilities (see likelihood_test_parallel.py)
	#events1 - the file that contains unfiltered events
	#events2 - the file that contains filtered events
	#outFile - the PDF file to generate
makeThrashingPlot = function(startDate, endDate, inFile, events1, events2, outFile){

	#Read the file
	t = read.csv(inFile)
	t$date = as.character(t$date)
	s = t[t$date>=startDate & t$date<=endDate,]
	
	#Set up the pdf
	print(paste("Creating", outFile))
	pdf(outFile, 12, 8)
	par(mfrow=c(2,1), mar=c(2,5,2,1), oma=c(1,1,4,1))


	#Add the probability plot with unfiltered events
	addOutlierPlot(s, t, "Original Events")
	addEvents(s, events1)
	#legend("bottomright", legend=c("M(t)", "Threshold"), col=c("black", "red"),
	#	  lwd=c(2,2), bg="white")

	#Add the probability plot with filtered events
	addOutlierPlot(s, t, "Merge Nearby Events")
	addEvents(s, events2)
	#legend("bottomright", legend=c("M(t)", "Threshold"), col=c("black", "red"),
	#	  lwd=c(2,2), bg="white")

	#Add overall title
	title("Event Detection - Thrashing", outer=T, cex.main=2)


}



plotGroup = function(prefix){
	makeplot("2012-10-21", "2012-11-11", sprintf("results/%s_outlier_scores.csv", prefix), sprintf("results/event_%s_Sandy_mahal.pdf", prefix), "Event Detection")
	makeplot("2010-12-20", "2011-01-09", sprintf("results/%s_outlier_scores.csv", prefix), sprintf("results/event_%s_Blizzard_mahal.pdf", prefix), "Event Detection")
	makeplot("2011-08-21", "2011-09-11", sprintf("results/%s_outlier_scores.csv", prefix), sprintf("results/event_%s_Irene_mahal.pdf", prefix), "Event Detection")
	makeplot("2013-02-03", "2013-02-24", sprintf("results/%s_outlier_scores.csv", prefix), sprintf("results/event_%s_Blizzard2_mahal.pdf", prefix), "Event Detection")
	makeplot("2010-02-21", "2010-03-14", sprintf("results/%s_outlier_scores.csv", prefix), sprintf("results/event_%s_Blizzard3_mahal.pdf", prefix), "Event Detection")
	makeplot("2013-10-06", "2013-10-27", sprintf("results/%s_outlier_scores.csv", prefix), sprintf("results/event_%s_October_mahal.pdf", prefix), "Event Detection")
}


dateToRange = function(dateStr){
	dt = strptime(dateStr, format="%Y-%m-%d %H:%M:%S")
	dt = strftime(dt, format="%Y-%m-%d")
	dt = strptime(dt, format="%Y-%m-%d")
	start = dt - 60*60*24*7
	end = dt + 60*60*24*14
	return(as.character(c(start,end)))
}



#makeLofPlot("2012-10-21", "2012-11-11", "results/outlier_scores.csv", "results/event_Sandy_lofs.pdf", "Event Detection")


#Make probability plots for several interesting events
if(F){
makeplot("2012-10-21", "2012-11-11", "results/outlier_scores.csv", "results/event_Sandy_mahal.pdf", "Event Detection")
makeplot("2010-12-20", "2011-01-09", "results/outlier_scores.csv", "results/event_Blizzard_mahal.pdf", "Event Detection")
makeplot("2011-08-21", "2011-09-11", "results/outlier_scores.csv", "results/event_Irene_mahal.pdf", "Event Detection")
makeplot("2013-02-03", "2013-02-24", "results/outlier_scores.csv", "results/event_Blizzard2_mahal.pdf", "Event Detection")
makeplot("2010-02-21", "2010-03-14", "results/outlier_scores.csv", "results/event_Blizzard3_mahal.pdf", "Event Detection")
makeplot("2013-10-06", "2013-10-27", "results/outlier_scores.csv", "results/event_October_mahal.pdf", "Event Detection")
}

#Make a plot to demonstrate thrashing
#makeThrashingPlot("2012-10-21", "2012-11-11", "results/outlier_scores.csv", "results/events_nomerge.csv", "results/events_sorted.csv", "results/thrashing.pdf")	



if(F){
	plotGroup("link_20_normalize")
	plotGroup("link_20_weighted_normalize")
	plotGroup("link_50_normalize")
	plotGroup("link_50_weighted_normalize")
	plotGroup("link_300_normalize")
	plotGroup("link_300_weighted_normalize")
}


if(T){
	t = read.csv("results/link_20_normalize_events_windowed.csv")
	pdf("results/lots_of_events.pdf")
	for(i in 1:20){
		rng = dateToRange(t$start_date[i])
		print(rng)
		makeplot(rng[1],rng[2], "blah", "[IGNORE]", "Event Detection")
	}
	dev.off()
}




