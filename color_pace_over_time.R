#Brian Donovan (briandonovan100@gmail.com)
#Creates colored plots which show the mean pace vector, or standardized pace vector


#These control the scope of the legend for standardized pace vectors
min_z = -2
max_z = 5

#These control the scope of the legend for mean pace vector
min_pace = 2
max_pace = 7




#Read the mean pace vectors
t = read.csv("features_imb20_k10/pace_features.csv")
t$Date=as.character(t$Date)





#Read the standardized pace vectors
zt = read.csv("results/coarse_features_imb20_k10_RPCAtune_10000000pcs_5percmiss_zscore.csv")
zt$Date=as.character(zt$Date)

#Create the color gradient ramp
#jet.colors =colorRamp(c("#00007F", "blue", "#007FFF", "cyan",
#                     "#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))


jet.colors =colorRamp(c("blue", "#007FFF", "cyan",
                     "#7FFF7F", "yellow", "#FF7F00", "red"))



#This function scales values from some arbitrary range, into the range (0,1)
#Values that fall outside of the given range are truncated at 0 or 1
#Arguments:
	#v - a value or list of values
	#lo - the min of the original range
	#hi - the max of the original range
#Returns: a vector of values between 0 and 1
linearScale = function(v, lo, hi){
	scaled = (v - lo)/(hi - lo)
	truncated = pmax(pmin(scaled, 1), 0)
	return (truncated)
}


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


#Adds a legend to the picture in a separate plot
#Arguments:
	#type - either "absolute" or "standard".  INdicates mean pace vectors or standardized pace vectors respectively
addLegend = function(type, crush=F){

	#Set up the margins
	par(mar=c(.1,0,1,0))
	

	if(crush){
		titleSize=.8
		axisSize=1
	}
	else{
		titleSize=.8
		axisSize=1
	}
	
	#Set up the plots - the type determines the title and the range of interesting values (lo, hi)
	if(type=="absolute"){
		lo = min_pace
		hi = max_pace
		value_granularity=15
		legend_granularity=1
		plot(0,0, type="n", xlim=c(lo,hi), ylim=c(0,1), xaxt="n", yaxt="n", , bty="n", cex.main=titleSize, main="Pace (min / mi)")
	}
	else if(type=="standardized"){
		lo = min_z
		hi = max_z
		value_granularity=10
		legend_granularity=1
		plot(0,0, type="n", xlim=c(lo,hi), ylim=c(0,1), xaxt="n", yaxt="n", , bty="n", cex.main=titleSize, main="Standardized Pace (Z-Score)")
	}




	vals = seq(lo, hi, 1/value_granularity)
	cvals = linearScale(vals, lo, hi)
	mycols = rgb(jet.colors(cvals)/255)
	a = c((0:((hi - lo)/legend_granularity))*value_granularity*legend_granularity + 1)
	print(vals)
	print(a)

        
        #y is constant
        yvals = rep(.6,length(vals))
        
        #Draw the squares
	points(vals, yvals, col=mycols, pch=15, cex=2)
	

	#Add the ticks and axis labels
	segments(x0=vals[a],y0=.4,x1=vals[a],y1=.8, lwd=2)
	text(x=vals[a],y=.2,labels=vals[a], cex=.8)
	
}


#Adds Hurricane-Sandy-related tags to the color plotj
#Arguments:
	#t - the main table, containing the pace vectors
addTags = function(t){
	
	#hvals = c(.9,.7,.9,.5,.8)
	#heights = minv + (maxv-minv)*hvals
	#segments(i,0,i,hvals, col="grey", lwd=3, lty=2)
	
	minv = 11.5
	maxv=16.5
	
	#2012-10-29,20:00:00,Sandy hits land,Atlantic City NJ
	i = match(TRUE, t$Date=="2012-10-29" & t$Hour==20)
	height = minv + (maxv-minv)*.50
	segments(i,0,i,height, col="grey", lwd=3, lty=1)
	text(i, height, "Sandy Hits Land", cex=.8)
	
	#2012-10-30,09:00:00,"Weather improves, cleanup begins",Entire city
	i = match(TRUE, t$Date=="2012-10-30" & t$Hour==9)
	height = minv + (maxv-minv)*.2
	segments(i,0,i,height, col="grey", lwd=3, lty=1)
	text(i, height, "Weather Improves", cex=.8)
	
	#2012-10-31,14:00:00,Partial metro service (commuter trains) resumes.,Grand Central & Penn 
	i = match(TRUE, t$Date=="2012-10-31" & t$Hour==14)
	height = minv + (maxv-minv)*.60
	segments(i,0,i,height, col="grey", lwd=3, lty=1)
	text(i, height, "Partial Metro\nService Resumes", cex=.8)
	
	#2012-11-01,?,HOV3+ carpooling restrictions begin.,Cars entering Manhattan between 6am and 12am. Except for GW bridge
	i = match(TRUE, t$Date=="2012-11-01" & t$Hour==2)
	height = minv + (maxv-minv)*.04
	segments(i,0,i,height, col="grey", lwd=3, lty=1)
	text(i, height, "Carpool Restrictions", cex=.8)
	
	#2012-11-02,19:00:00,Power restored,Most of Lower Manhattan
	i = match(TRUE, t$Date=="2012-11-02" & t$Hour==19)
	height = minv + (maxv-minv)*.3
	segments(i,0,i,height, col="grey", lwd=3, lty=1)
	text(i, height, "Power Restored", cex=.8)
	
	i = match(TRUE, t$Date=="2012-11-04" & t$Hour==9)
	height = minv + (maxv-minv)*.45
	segments(i,0,i,height, col="grey", lwd=3, lty=1)
	text(i, height, "NYC Marathon", cex=.8)
	
	i = match(TRUE, t$Date=="2012-11-07" & t$Hour==19)
	height = minv + (maxv-minv)*.3
	segments(i,0,i,height, col="grey", lwd=3, lty=1)
	text(i, height, "Snow Storm", cex=.8)
	
}



addColorRow = function(vals, height, type){
        #Iterate through columns (dimensions of mean pace vector)
        #Each column corresponds to a trip type (E->M for example)

		
		#Symbol types and line types for each dot
		#Default is squares with no lines
		mypch = rep(15, length(vals))
		mylwd = rep(0, length(vals))
        
	  	
	  	#convert values into colors - range depends on plot type
		if(type=="absolute"){
			mycols = rgb(jet.colors(linearScale(vals/60, min_pace, max_pace))/256)
		}
		else if(type=="standardized"){
			mycols = rgb(jet.colors(linearScale(vals, min_z, max_z))/256)
	  	}
	  
	  #Missing data (values of zero) are plotted as black Xs
	  mycols[vals==0] = "black"
	  mypch[vals==0] = 4
	  mylwd[vals==0] = 1.1
	  

	  
	  #Draw the points
	  points(x=1:length(vals), y=rep(height, length(vals)), col = mycols,
		pch=mypch, lwd=mylwd, cex=.8)

}

#Plots pace vectors for a period of time.  The dimensions are stacked vertically and the pace/zscore is indicated by the color
#Arguments:
	#startDate - the beginning of the desired time range to plot
	#endDate - the end of the desired time range to plot
	#mainTitle - the title of the plot
	#type - either "absolute" or "standardized"
	#crus - if True, the plot will be "crushed" to fit more information

makeMainPlot = function(startDate, endDate, mainTitle, type, crush=F){


	if(crush){
		par(mar=c(1,3,1,.4))	#Decrease margins
		extra_height=0		#Don't leave room for tags
		pt_size = .8		#Control size of plotted points
		region_label_size = 2	#Control size of y axis label
		mainTitleSize=1
		mainTitle = ""		#No main title
		s = t[t$Date>=startDate & t$Date <= endDate,]
	}
	else{
		par(mar=c(3,4,2,.4))	#Large margins
		extra_height=6		#Leave 5 rows empty for tags
		pt_size = 1		#Control size of y axis label
		mainTitleSize=1
		s = zt[zt$Date>=startDate & zt$Date <= endDate,]
		
	}
	
	#Create the plot
	plot(0,0, type="n", xlim=c(7,(24*7 - 7)), ylim=c(1,10.5+extra_height),
		xaxt="n", xlab="", yaxt="n", ylab="", main=mainTitle, cex.main=mainTitleSize)

	# Add the necessary rows
	addColorRow(s$r0.r0, 10.5, type)
	addColorRow(s$r6.r6, 9.5, type)
	addColorRow(s$r4.r4, 8.5, type)
	addColorRow(s$r7.r7, 7.5, type)
	addColorRow(s$r6.r4, 6, type)
	addColorRow(s$r4.r6, 5, type)
	addColorRow(s$r0.r1, 4, type)
	addColorRow(s$r1.r0, 3, type)
	addColorRow(s$r0.r7, 2, type)
	addColorRow(s$r7.r0, 1, type)

	#abline(h=6.5, lwd=3, lty=2)
	

	
	#Add tags if necessary
	addTags(s)
	
	
	

	#X axis labels appear on the midnights (hour 1, 25, 49, ...)	
	a=(0:6)*24 + 1

	short_dates = shortenDates(s$Date)
	
	if(crush){
		axis(1, at=a, labels=short_dates[a], cex.axis=1, pos=2.5, lty=0)
	}
	else{
		axis(1, at=a, labels=short_dates[a], cex.axis=1, pos=0)
	}
	
	
	#Zones = Y axis labels
	y_at=c(10.5,9.5,8.5,7.5, 6:1)
	zones = rev(c("0-0","6-6","4-4","7-7","6-4","4-6","0-1","1-0","0-7","7-0"))
	axis(2, at=y_at, labels=rev(zones), las=1, cex.axis=.7)
	
	
	#Draw horizontal lines between each group of rows (a group is a set of zones with the same origin)

	
	#Draw vertical lines on the midnights
	segments(a,0,a,16.5)


}


#Produces a plot with a colored mean pace vector and a legend
#Arguments:
	#startDate - the beginning of the desired time range to plot
	#endDate - the end of the desired time range to plot
	#mainTitle - the title of the plot
	#type - either "absolute" or "standardized"
plotTimeSpan = function(startDate, endDate, mainTitle, type){
	print(mainTitle)
	
	#Setup the layout - a tall graph on top and a short graph on the bottom for the legend
	layout(matrix(c(1,2),2), heights=c(10,3))
	
	#Make the main plot in the first plot
	makeMainPlot(startDate, endDate, mainTitle, type)
	
	#Add the legend in the second plot
	addLegend(type)
	
}


#Produces a plot with three weeks of mean pace vectors and a legend
#Arguments:
	#weekDates - A vector of consecutive Sunday dates (strings).  Should contain 4 dates, which divide up the three weeks
	#type - either "absolute" or "standardized"
plot3Weeks = function(weekDates, type){
	#Layout contains 4 plots - 3 big ones for the main plots, and 1 small one for the legend
	layout(matrix(1:4,4), heights=c(4,4,4,2))
	
	#Add the first 3 main plots
	for(i in 1:3){
		print(weekDates[i])
		makeMainPlot(weekDates[i], weekDates[i+1], weekDates[i], type, crush=T)
	}

	#Add the legend in the last plot  
	addLegend(type, crush=T)
	
	#Add an overall title
	title(main="Mean Pace Vector - Three Typical Weeks", outer=T, cex.main=2)
}


#Produces a plot with three weeks of mean pace vectors and a legend
#Arguments:
	#weekDates - A vector of consecutive Sunday dates (strings).  Should contain 4 dates, which divide up the three weeks
	#type - either "absolute" or "standardized"
plot1Week = function(weekDates, type){
	#Layout contains 4 plots - 3 big ones for the main plots, and 1 small one for the legend
	layout(matrix(1:2,2), heights=c(2, 1))
	
	#Add the first 3 main plots
	makeMainPlot(weekDates[1], weekDates[2], weekDates[1], type, crush=T)


	#Add the legend in the last plot  
	addLegend(type, crush=T)
	
	#Add an overall title
	title(main="Origin-Destination Paces during a Typical Week", outer=T, cex.main=1)
}


###########################################################################################
############################## MAIN CODE BEGINS HERE ######################################
###########################################################################################


if(T){
	#Create standardized pace vector plot for week of Hurricane Sandy
	pdf("results/color_standardized_pace_over_time.pdf", 10, 3)
	plotTimeSpan("2012-10-28", "2012-11-04", "Standardized Pace (min/mi) Over Time - Week of Hurricane Sandy", "standardized")
	dev.off()
}


#Optional - make plot for whole year (relatively slow)
plotWholeYear = F
if(plotWholeYear){
	#These are all of the Sundays
 	weeks = c('2010-01-03', '2010-01-10', '2010-01-17', '2010-01-24', '2010-01-31', '2010-02-07', '2010-02-14', '2010-02-21', '2010-02-28', '2010-03-07', '2010-03-14', '2010-03-21', '2010-03-28', '2010-04-04', '2010-04-11', '2010-04-18', '2010-04-25', '2010-05-02', '2010-05-09', '2010-05-16', '2010-05-23', '2010-05-30', '2010-06-06', '2010-06-13', '2010-06-20', '2010-06-27', '2010-07-04', '2010-07-11', '2010-07-18', '2010-07-25', '2010-08-01', '2010-08-08', '2010-08-15', '2010-08-22', '2010-08-29', '2010-09-05', '2010-09-12', '2010-09-19', '2010-09-26', '2010-10-03', '2010-10-10', '2010-10-17', '2010-10-24', '2010-10-31', '2010-11-07', '2010-11-14', '2010-11-21', '2010-11-28', '2010-12-05', '2010-12-12', '2010-12-19', '2010-12-26', '2011-01-02', '2011-01-09', '2011-01-16', '2011-01-23', '2011-01-30', '2011-02-06', '2011-02-13', '2011-02-20', '2011-02-27', '2011-03-06', '2011-03-13', '2011-03-20', '2011-03-27', '2011-04-03', '2011-04-10', '2011-04-17', '2011-04-24', '2011-05-01', '2011-05-08', '2011-05-15',
  '2011-05-22', '2011-05-29', '2011-06-05', '2011-06-12', '2011-06-19', '2011-06-26', '2011-07-03', '2011-07-10', '2011-07-17', '2011-07-24', '2011-07-31', '2011-08-07', '2011-08-14', '2011-08-21', '2011-08-28', '2011-09-04', '2011-09-11', '2011-09-18', '2011-09-25', '2011-10-02', '2011-10-09', '2011-10-16', '2011-10-23', '2011-10-30', '2011-11-06', '2011-11-13', '2011-11-20', '2011-11-27', '2011-12-04', '2011-12-11', '2011-12-18', '2011-12-25', '2012-01-01', '2012-01-08', '2012-01-15', '2012-01-22', '2012-01-29', '2012-02-05', '2012-02-12', '2012-02-19', '2012-02-26', '2012-03-04', '2012-03-11', '2012-03-18', '2012-03-25', '2012-04-01', '2012-04-08', '2012-04-15', '2012-04-22', '2012-04-29', '2012-05-06', '2012-05-13', '2012-05-20', '2012-05-27', '2012-06-03', '2012-06-10', '2012-06-17', '2012-06-24', '2012-07-01', '2012-07-08', '2012-07-15', '2012-07-22', '2012-07-29', '2012-08-05', '2012-08-12', '2012-08-19', '2012-08-26', '2012-09-02', '2012-09-09', '2012-09-16', '2012-09-23', '2012-09-30', '2012-10-07',
  '2012-10-14', '2012-10-21', '2012-10-28', '2012-11-04', '2012-11-11', '2012-11-18', '2012-11-25', '2012-12-02', '2012-12-09', '2012-12-16', '2012-12-23', '2012-12-30', '2013-01-06', '2013-01-13', '2013-01-20', '2013-01-27', '2013-02-03', '2013-02-10', '2013-02-17', '2013-02-24', '2013-03-03', '2013-03-10', '2013-03-17', '2013-03-24', '2013-03-31', '2013-04-07', '2013-04-14', '2013-04-21', '2013-04-28', '2013-05-05', '2013-05-12', '2013-05-19', '2013-05-26', '2013-06-02', '2013-06-09', '2013-06-16', '2013-06-23', '2013-06-30', '2013-07-07', '2013-07-14', '2013-07-21', '2013-07-28', '2013-08-04', '2013-08-11', '2013-08-18', '2013-08-25', '2013-09-01', '2013-09-08', '2013-09-15', '2013-09-22', '2013-09-29', '2013-10-06', '2013-10-13', '2013-10-20', '2013-10-27', '2013-11-03', '2013-11-10', '2013-11-17', '2013-11-24', '2013-12-01', '2013-12-08', '2013-12-15', '2013-12-22', '2013-12-29')
  
  #Plot each week on a separate page of the PDF
  pdf("results/color_standardized_pace_whole_year.pdf", 10, 5)
  for(i in 1:(length(weeks)-1)){
    startdate = weeks[i]
    enddate = weeks[i+1]
    title = paste("Week of",startdate)
    plotTimeSpan(startdate, enddate, title, "standardized")
  }

  dev.off()
}


if(F){
	#Make plot of mean pace vector for "3 typical weeks"
	#pdf("results/color_pace_3weeks.pdf", 5, 5)
	svg("results/color_pace_3weeks.svg", 10, 5)
	weeks=c('2010-04-04', '2010-04-11', '2010-04-18', '2010-04-25')
	par(oma=c(1,1,2,1))

	plot3Weeks(weeks, 'absolute')
	dev.off()
}

pdf("results/color_pace_1week.pdf", 10, 2)
#weeks=c('2010-04-04', '2010-04-11')
weeks=c('2011-03-06', '2011-03-13')
par(oma=c(.1,.1,.7,.1))
plot1Week(weeks, 'absolute')
dev.off()


pdf("results/color_sandy_1week.pdf", 10, 2)
weeks=c("2012-10-28", "2012-11-04")
par(oma=c(.1,.1,.7,.1))
plot1Week(weeks, 'absolute')
dev.off()

