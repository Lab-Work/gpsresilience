min_z = -5
max_z = 5


t = read.csv("4year_features/pace_features.csv")
zt = read.csv("results/std_pace_vector.csv")

jet.colors =colorRamp(c("#00007F", "blue", "#007FFF", "cyan",
                     "#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))


linearScale = function(v, lo, hi){
	scaled = (v - lo)/(hi - lo)
	truncated = pmax(pmin(scaled, 1), 0)
	return (truncated)
}



shortenDates = function(dates){
	mydates = dates
	  mydates = strptime(mydates, '%Y-%m-%d')
	  mydates = format(mydates, '%m-%d')
	  return(mydates)
}


addLegend = function(type){


	par(mar=c(2,0,.5,0))
	#par(mar=c(0,0,0,0))
	if(type=="absolute"){
		plot(0,0, type="n", xlim=c(1,200), ylim=c(-1,1), xaxt="n", yaxt="n", , bty="n", cex.main=.8, main="Pace (min / mi)")
		lo = 0
		hi = 600
	}
	else if(type=="standardized"){
		plot(0,0, type="n", xlim=c(1,200), ylim=c(-1,1), xaxt="n", yaxt="n", , bty="n", cex.main=.8, main="Standardized Pace (Z-Score)")
		lo = min_z
		hi = max_z
	}


	#par(mar=c(0,0,0,0))
	jet.colors =colorRamp(c("#00007F", "blue", "#007FFF", "cyan",
                     "#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))
        vals = seq(lo, hi, length=201)
        mycols = rgb(jet.colors(linearScale(vals, lo,hi))/256)
        yvals = rep(0,200)
	points(1:200, yvals, col=mycols, pch=15, cex=2)
	
	a = (0:10)*20 + 1
	#print(a)
	#print(vals[a])
	if(type=="absolute"){
	  axis(1, at=a, labels=round(vals[a]/60, 2))
	}
	else if(type=="standardized"){
	   axis(1, at=a, labels=round(vals[a], 2))
	}
	
}



addTags = function(t){
	
	#hvals = c(.9,.7,.9,.5,.8)
	#heights = minv + (maxv-minv)*hvals
	#segments(i,0,i,hvals, col="grey", lwd=3, lty=2)
	
	minv = 17
	maxv=26
	
	#2012-10-29,20:00:00,Sandy hits land,Atlantic City NJ
	i = match(TRUE, t$Date=="2012-10-29" & t$Hour==20)
	height = minv + (maxv-minv)*.45
	segments(i,0,i,height, col="grey", lwd=3, lty=1)
	text(i, height, "Sandy Hits Land", cex=.8)
	
	#2012-10-30,09:00:00,"Weather improves, cleanup begins",Entire city
	i = match(TRUE, t$Date=="2012-10-30" & t$Hour==9)
	height = minv + (maxv-minv)*.2
	segments(i,0,i,height, col="grey", lwd=3, lty=1)
	text(i, height, "Weather Improves", cex=.8)
	
	#2012-10-31,14:00:00,Partial metro service (commuter trains) resumes.,Grand Central & Penn 
	i = match(TRUE, t$Date=="2012-10-31" & t$Hour==14)
	height = minv + (maxv-minv)*.4
	segments(i,0,i,height, col="grey", lwd=3, lty=1)
	text(i, height, "Partial Metro\nService Resumes", cex=.8)
	
	#2012-11-01,?,HOV3+ carpooling restrictions begin.,Cars entering Manhattan between 6am and 12am. Except for GW bridge
	i = match(TRUE, t$Date=="2012-11-01" & t$Hour==0)
	height = minv + (maxv-minv)*.1
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


makeMainPlot = function(startDate, endDate, mainTitle, type, crush=F){


	if(crush){
	  par(mar=c(1,3,1,.4))
	  extra_height=0
	  pt_size = .7
	  region_label_size = 2
	  mainTitle = ""
	}
	else{
	  par(mar=c(3,4,2,.4))
	  extra_height=5
	  pt_size = .7
	}
	plot(0,0, type="n", xlim=c(7,(24*7 - 7)), ylim=c(1,16+extra_height), xaxt="n", xlab="", yaxt="n", ylab="", main=mainTitle)

	

	
	
	if(type=="absolute"){
		vals = t$sandy
		mycols = rgb(jet.colors(linearScale(vals, 100, 600))/256)
		s = t[as.character(t$Date) >= startDate & as.character(t$Date) < endDate,]
		
        }
        if(type=="standardized"){
        	vals = (t$sandy - t$avg) / t$sdev
        	mycols = rgb(jet.colors(linearScale(vals, min_z, max_z))/256)
        	s = zt[as.character(zt$Date) >= startDate & as.character(zt$Date) < endDate,]
        	
        }
        
        
        for(colid in 4:ncol(s)){
	  
	  vals = s[,colid]
	  #print(names(s)[colid])
	  mypch = rep(15, length(vals))
	  mylwd = rep(0, length(vals))
        
	  
	  if(type=="absolute"){
	  	mycols = rgb(jet.colors(linearScale(vals, 100, 600))/256)
	  }
	  else if(type=="standardized"){
		mycols = rgb(jet.colors(linearScale(vals, min_z, max_z))/256)
	  }
	  
	  
	  mycols[vals==0] = "black"
	  mypch[vals==0] = 4
	  mylwd[vals==0] = 1.1
	  
	  yvals = rep(20 - colid, nrow(t))
	  
	  
	  points(x=1:nrow(t), y=yvals, col = mycols, pch=mypch, lwd=mylwd, cex=pt_size)
	}
	
	
	addTags(s)
	
	
	

	
	a=(0:6)*24 + 1
	#if(crush){
	  #axis(1, at=a, labels=s$Date[a],las=1, cex.axis=.7)
	#}
	#else{
	#  mydates = s$Date[a]
	#  mydates = strptime(mydates, '%Y-%m-%d')
	#  mydates = format(mydates, '%m-%d')
	#  
	#  axis(1, at=a, labels=mydates,las=3, cex.axis=.7)
	#}
	short_dates = shortenDates(s$Date)
	
	if(crush){
		axis(1, at=a, labels=short_dates[a], cex.axis=.7, pos=2.5)
	}
	else{
		axis(1, at=a, labels=short_dates[a], cex.axis=1, pos=0)
	}
	
	
		zones = c("E-E","E-U","E-M","E-L","U-E","U-U","U-M","U-L","M-E","M-U","M-M","M-L","L-E","L-U","L-M","L-L")

	axis(2, at=1:16, labels=rev(zones), las=1, cex.axis=.7)
	
	
	for (i in 1:4){
		abline(h=i*4+.5)
	}
	
	segments(a,0,a,16.5)


}



plotTimeSpan = function(startDate, endDate, mainTitle, type){
	print(mainTitle)
	layout(matrix(c(1,2),2), heights=c(10,2))
	
	
	makeMainPlot(startDate, endDate, mainTitle, type)
	
	addLegend(type)
	
}



plot3Weeks = function(weekDates, type){
  layout(matrix(1:4,4), heights=c(4,4,4,2))
  for(i in 1:3){
    print(weekDates[i])
    makeMainPlot(weekDates[i], weekDates[i+1], weekDates[i], "absolute", crush=T)
    #a=(0:6)*24 + 1
    #axis(side=1, at=a, labels=c("Su","M", "Tu", "W","Th", "F", "Sa"), pos=2.5, line=NA)
  }
  
  addLegend(type)
  title(main="Mean Pace Vector - Three Typical Weeks", outer=T)
}


ctrl = 1


if(ctrl==1){
  #svg("results/color_standardized_pace_over_time.svg",8.5, 5.5)
  pdf("results/color_standardized_pace_over_time.pdf", 8.5, 4.5)
  #plotTimeSpan("2012-10-14", "2012-10-21", "Standardized Pace (sec/mi) Over Time - 2 Weeks Before Sandy", "standardized")
  #plotTimeSpan("2012-10-21", "2012-10-28", "Standardized Pace (sec/mi) Over Time - 1 Week Before Sandy", "standardized")
  plotTimeSpan("2012-10-28", "2012-11-04", "Standardized Pace (sec/mi) Over Time - Week of Hurricane Sandy", "standardized")
  #plotTimeSpan("2012-11-04", "2012-11-11", "Standardized Pace (sec/mi) Over Time - 1 Week After Sandy", "standardized")
  #plotTimeSpan("2012-11-11", "2012-11-18", "Standardized Pace (sec/mi) Over Time - 2 Weeks After Sandy", "standardized")
  dev.off()


  svg("results/color_pace_over_time.svg",8.5, 5.5)
  #plotTimeSpan("2012-10-14", "2012-10-21", "Pace (sec/mi) Over Time - 2 Weeks Before Sandy", "absolute")
  #plotTimeSpan("2012-10-21", "2012-10-28", "Pace (sec/mi) Over Time - 1 Week Before Sandy", "absolute")
  plotTimeSpan("2012-10-28", "2012-11-04", "Pace (sec/mi) Over Time - Week of Sandy", "absolute")
  #plotTimeSpan("2012-11-04", "2012-11-11", "Pace (sec/mi) Over Time - 1 Week After Sandy", "absolute")
  #plotTimeSpan("2012-11-11", "2012-11-18", "Pace (sec/mi) Over Time - 2 Weeks After Sandy", "absolute")
  dev.off()
}


ctrl=2
if(ctrl==2){
  #weeks = c("2012-01-01","2012-01-08","2012-01-15","2012-01-22","2012-01-29","2012-02-05","2012-02-12","2012-02-19","2012-02-26","2012-03-04","2012-03-11","2012-03-18","2012-03-25","2012-04-01","2012-04-08","2012-04-15","2012-04-22","2012-04-29","2012-05-06","2012-05-13","2012-05-20","2012-05-27","2012-06-03","2012-06-10","2012-06-17","2012-06-24","2012-07-01","2012-07-08","2012-07-15","2012-07-22","2012-07-29","2012-08-05","2012-08-12","2012-08-19","2012-08-26","2012-09-02","2012-09-09","2012-09-16","2012-09-23","2012-09-30","2012-10-07","2012-10-14","2012-10-21","2012-10-28","2012-11-04","2012-11-11","2012-11-18","2012-11-25","2012-12-02","2012-12-09","2012-12-16","2012-12-23","2012-12-30")
  weeks = c('2010-01-03', '2010-01-10', '2010-01-17', '2010-01-24', '2010-01-31', '2010-02-07', '2010-02-14', '2010-02-21', '2010-02-28', '2010-03-07', '2010-03-14', '2010-03-21', '2010-03-28', '2010-04-04', '2010-04-11', '2010-04-18', '2010-04-25', '2010-05-02', '2010-05-09', '2010-05-16', '2010-05-23', '2010-05-30', '2010-06-06', '2010-06-13', '2010-06-20', '2010-06-27', '2010-07-04', '2010-07-11', '2010-07-18', '2010-07-25', '2010-08-01', '2010-08-08', '2010-08-15', '2010-08-22', '2010-08-29', '2010-09-05', '2010-09-12', '2010-09-19', '2010-09-26', '2010-10-03', '2010-10-10', '2010-10-17', '2010-10-24', '2010-10-31', '2010-11-07', '2010-11-14', '2010-11-21', '2010-11-28', '2010-12-05', '2010-12-12', '2010-12-19', '2010-12-26', '2011-01-02', '2011-01-09', '2011-01-16', '2011-01-23', '2011-01-30', '2011-02-06', '2011-02-13', '2011-02-20', '2011-02-27', '2011-03-06', '2011-03-13', '2011-03-20', '2011-03-27', '2011-04-03', '2011-04-10', '2011-04-17', '2011-04-24', '2011-05-01', '2011-05-08', '2011-05-15',
  '2011-05-22', '2011-05-29', '2011-06-05', '2011-06-12', '2011-06-19', '2011-06-26', '2011-07-03', '2011-07-10', '2011-07-17', '2011-07-24', '2011-07-31', '2011-08-07', '2011-08-14', '2011-08-21', '2011-08-28', '2011-09-04', '2011-09-11', '2011-09-18', '2011-09-25', '2011-10-02', '2011-10-09', '2011-10-16', '2011-10-23', '2011-10-30', '2011-11-06', '2011-11-13', '2011-11-20', '2011-11-27', '2011-12-04', '2011-12-11', '2011-12-18', '2011-12-25', '2012-01-01', '2012-01-08', '2012-01-15', '2012-01-22', '2012-01-29', '2012-02-05', '2012-02-12', '2012-02-19', '2012-02-26', '2012-03-04', '2012-03-11', '2012-03-18', '2012-03-25', '2012-04-01', '2012-04-08', '2012-04-15', '2012-04-22', '2012-04-29', '2012-05-06', '2012-05-13', '2012-05-20', '2012-05-27', '2012-06-03', '2012-06-10', '2012-06-17', '2012-06-24', '2012-07-01', '2012-07-08', '2012-07-15', '2012-07-22', '2012-07-29', '2012-08-05', '2012-08-12', '2012-08-19', '2012-08-26', '2012-09-02', '2012-09-09', '2012-09-16', '2012-09-23', '2012-09-30', '2012-10-07',
  '2012-10-14', '2012-10-21', '2012-10-28', '2012-11-04', '2012-11-11', '2012-11-18', '2012-11-25', '2012-12-02', '2012-12-09', '2012-12-16', '2012-12-23', '2012-12-30', '2013-01-06', '2013-01-13', '2013-01-20', '2013-01-27', '2013-02-03', '2013-02-10', '2013-02-17', '2013-02-24', '2013-03-03', '2013-03-10', '2013-03-17', '2013-03-24', '2013-03-31', '2013-04-07', '2013-04-14', '2013-04-21', '2013-04-28', '2013-05-05', '2013-05-12', '2013-05-19', '2013-05-26', '2013-06-02', '2013-06-09', '2013-06-16', '2013-06-23', '2013-06-30', '2013-07-07', '2013-07-14', '2013-07-21', '2013-07-28', '2013-08-04', '2013-08-11', '2013-08-18', '2013-08-25', '2013-09-01', '2013-09-08', '2013-09-15', '2013-09-22', '2013-09-29', '2013-10-06', '2013-10-13', '2013-10-20', '2013-10-27', '2013-11-03', '2013-11-10', '2013-11-17', '2013-11-24', '2013-12-01', '2013-12-08', '2013-12-15', '2013-12-22', '2013-12-29')
  
  pdf("results/color_standardized_pace_whole_year.pdf", 10, 5)
  for(i in 1:(length(weeks)-1)){
    startdate = weeks[i]
    enddate = weeks[i+1]
    title = paste("Week of",startdate)
    plotTimeSpan(startdate, enddate, title, "standardized")
  }

  dev.off()
}
ctrl=3
if(ctrl==3){
  pdf("results/color_pace_3weeks.pdf", 5, 5)
  #svg("presentation_figs/color_pace_3weeks.svg", 10, 10)
  weeks=c('2010-04-04', '2010-04-11', '2010-04-18', '2010-04-25')
  par(oma=c(1,1,2,1))
  
  plot3Weeks(weeks, 'absolute')
  dev.off()
}
