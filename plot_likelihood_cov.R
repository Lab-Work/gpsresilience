events = read.csv("results/detected_events_1tail.csv")
events$StartDate = as.character(events$StartDate)
events$EndDate = as.character(events$EndDate)


shortenDates = function(dates){
	mydates = dates
	  mydates = strptime(mydates, '%Y-%m-%d')
	  mydates = format(mydates, '%m-%d')
	  return(mydates)
}


addEvents = function(s, ylm, filename){

	s_dates = strptime(as.character(s$date), "%Y-%m-%d") + s$hour*3600
	MIN_DATE = min(s_dates)
	MAX_DATE = max(s_dates)

	print(MIN_DATE)
	events = read.csv(filename)
	events$start_date = strptime(as.character(events$start_date), "%Y-%m-%d %H:%M:%S")
	events$end_date = strptime(as.character(events$end_date), "%Y-%m-%d %H:%M:%S")


	start_x = difftime(events$start_date, MIN_DATE, units="hours")
	end_x = difftime(events$end_date, MIN_DATE, units="hours")


		
	for (i in 1:length(start_x)){
		if(start_x[i] > 0 && end_x[i] < 3*7*24){
			polygon(x=c(start_x[i], end_x[i], end_x[i], start_x[i]), y=c(ylm[1], ylm[1], ylm[2], ylm[2]), col=rgb(.5,.5,.5,.4))
		}
	}
	


}


addPacePlot = function(s){


  print(dim(s))
  print(dim(s))
  plot(0,0, type="n", main="Pace Comparison", xaxt="n", xlab="", ylab="Pace (min/mi)", xlim=c(1,nrow(s)), ylim=c(2,9), lwd=2)

  
  
  
  polygon(x=c(1:nrow(s), rev(1:nrow(s))), y = c(s$expected_pace/60 - s$sd_pace/60, rev(s$expected_pace/60 + s$sd_pace/60)), col=rgb(.5,.5,.8), border=NA)
  lines(s$expected_pace/60 - s$sd_pace/60, col=rgb(.4,.4,.4), lwd=2)
  lines(s$expected_pace/60 + s$sd_pace/60, col=rgb(.4,.4,.4), lwd=2)
  
  
  for(i in 1:(nrow(s)-1)){
	  if(s$global_pace[i] < s$expected_pace[i]){
		  mycol = "green"
	  }
	  else{
		  mycol = "red"
	  }
	  	
	  polygon(x=c(i, i+1, i+1, i), y=c(s$expected_pace[i]/60, s$expected_pace[i+1]/60, s$global_pace[i+1]/60, s$global_pace[i]/60), col=mycol, border=mycol)
  }


  lines(s$global_pace/60, col="black", lwd=3)
  lines(s$expected_pace/60, col="blue", lwd=3)
  
  

  
  
  
  ids = (0:20) * 24 + 1
  #axis(1, at=ids, labels=s$date[ids], las=3, cex.axis=.7)
  print("y")
  #weekdays = rep(c("Su","M","Tu","W","Th","F","Sa"),3)
  #axis(1, at=ids, labels=weekdays)
  short_dates = shortenDates(s$date)
  axis(1, at=ids, labels=short_dates[ids], cex.axis=.75)
  
  print("z")
  abline(v=ids)
  ids2 = (0:3)*24*7 + 1
  abline(v=ids2, lwd=3)



  #addEvents(s, c(100,500))

  legend("topright", legend=c("ObsPace", "AvgPace", "1 StDev"), col=c("black", "blue", rgb(.4,.4,.4)), lwd=2, lty=1, bg="white")

}


addProbPlot = function(s, t, title, type="full"){

		print(dim(s))
		print(names(s))
	if(type=="full"){
		s_lnl = s$full_lnl
		t_lnl = t$full_lnl
	}
	else if(type=="kern"){
		s_lnl = s$kern_lnl
		t_lnl = t$kern_lnl	
	}
	  plot(s_lnl, col="black", type="l", main=title, ylim = quantile(s_lnl, c(.002,1)), xaxt="n", xlab="", ylab="Relative Log-Probability Density", lwd=2)
	 # lines(s$ind_lnl, col="blue", lwd=1)
	#  lines(s$param_lnl, col="red", lwd=1)
	  filtered_p = t_lnl[t_lnl < 0]
	  abline(h=quantile(filtered_p, .05), col="red", lwd=2)
	  ids = (0:20) * 24 + 1
	  
	  #weekdays = rep(c("Su","M","Tu","W","Th","F","Sa"),3)
	  #axis(1,at=ids, labels= weekdays)
	  
	  short_dates = shortenDates(s$date)
	  axis(1, at=ids, labels=short_dates[ids], cex.axis=.75)
	  
	  
	  
	  abline(v=ids)
	  ids2 = (0:3)*24*7 + 1
	  abline(v=ids2, lwd=3)
	  #lines(s$lnl_smooth, col="blue", lwd=3)




	  #lines(s$lnl_lognorm, col="purple", type="l", xaxt="n", xlab="", ylab="Log-Likelihood")
	  #ids = (0:21) * 24 + 1
	  #axis(1, at=ids, labels=s$date[ids], las=3, cex.axis=.7)
	  #lines(s$lnl_lognorm_smooth, col="darkgreen", lwd=2)



	  #addEvents(s, range(s$lnl_norm))

	  legend("bottomright", legend=c("R(t)", "Threshold"), col=c("black", "red"),
		  lwd=c(2,2), bg="white")
}





makeplot = function(startDate, endDate, outFile, title){


  inFile = "results/lnl_over_time_leave1.csv"
  inFile2 = "results/lnl_over_time_shrink_leave1.csv"
  
  print(paste("Creating", outFile))
  pdf(outFile, 12, 8)
  par(mfrow=c(2,1), mar=c(3,5,2,1))

  #lnl plot
  t = read.csv(inFile)
  t$date = as.character(t$date)
  s = t[t$date>=startDate & t$date<=endDate,]

	
  addProbPlot(s, t, title)
 

  addPacePlot(s)


  DO_SHRINKAGE=F
  if(DO_SHRINKAGE){

    ###################################################################################################


    t = read.csv(inFile2)
    t$date = as.character(t$date)
    s = t[t$date>="2012-10-21" & t$date<="2012-11-11",]

    
    print(dim(t))
    print(dim(s))
    jet.colors =colorRamp(c("#00007F", "blue", "#007FFF", "cyan",
			"#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))


    plot(0,0,type="n", xlim=c(0,nrow(s)), ylim=range(s[,4:14]), main="Shrinkage Estimation")
    shrinkCoefs = (0:10)/10
    for(i in 1:11){
      colid = i + 3
      mycol = rgb(jet.colors(shrinkCoefs[i])/256)
      lines(s[,colid], col=mycol)
    }

    legend("bottomright", legend=shrinkCoefs, col=rgb(jet.colors(shrinkCoefs)/256), title="Shrinkage Coefficient", lwd=2)

    addPacePlot()
  }
  dev.off()
}


makeKernPlot = function(startDate, endDate, outFile, title){
	 inFile = "results/lnl_over_time_leave1.csv"
  inFile2 = "results/lnl_over_time_shrink_leave1.csv"
  
  print(paste("Creating", outFile))
  pdf(outFile, 12, 8)
  par(mfrow=c(2,1), mar=c(3,5,2,1))

  #lnl plot
  t = read.csv(inFile)
  t$date = as.character(t$date)
  s = t[t$date>=startDate & t$date<=endDate,]

	
	addProbPlot(s, t, title, type="full")
 

	addPacePlot(s)
  
	
	addProbPlot(s, t, title, type="kern")
 

	addPacePlot(s)
	
	
	
	dev.off()
	
}



makeThrashingPlot = function(startDate, endDate, events1, events2, events3, outFile){
	inFile = "results/lnl_over_time_leave1.csv"
	inFile2 = "results/lnl_over_time_shrink_leave1.csv"
	  
	print(paste("Creating", outFile))
	pdf(outFile, 12, 8)
	par(mfrow=c(2,1), mar=c(2,5,2,1), oma=c(1,1,4,1))

	#lnl plot
	t = read.csv(inFile)
	t$date = as.character(t$date)
	s = t[t$date>=startDate & t$date<=endDate,]

	addProbPlot(s, t, "Original Events")
	addEvents(s, quantile(s$full_lnl, c(.002,1)), events1)
	legend("bottomright", legend=c("R(t)", "Threshold"), col=c("black", "red"),
		  lwd=c(2,2), bg="white")

	addProbPlot(s, t, "Merge Nearby Events")
	addEvents(s, quantile(s$full_lnl, c(.002,1)), events2)
	legend("bottomright", legend=c("R(t)", "Threshold"), col=c("black", "red"),
		  lwd=c(2,2), bg="white")

	
	title("Event Detection - Thrashing", outer=T, cex.main=2)


}



#makeplot("results/lnl_over_time_cov.csv", "results/lnl_over_time_shrink.csv", "results/likelihood_cov.pdf", "Log-Likelihood Test")
#makeplot("results/expected_lnl_over_time_cov.csv", "results/expected_lnl_over_time_shrink.csv", "results/expected_likelihood_cov.pdf", "Expected Log-Likelihood Test")
ctrl = 1
if(ctrl==1){

	makeplot("2012-10-21", "2012-11-11", "results/likelihood_leave1.pdf", "Event Detection")
	makeplot("2010-12-20", "2011-01-09", "results/event_Blizzard.pdf", "Event Detection")
	makeplot("2011-08-21", "2011-09-11", "results/event_Irene.pdf", "Event Detection")
	makeplot("2013-02-03", "2013-02-24", "results/event_Blizzard2.pdf", "Event Detection")
	makeplot("2010-02-21", "2010-03-14", "results/event_Blizzard3.pdf", "Event Detection")
	makeplot("2013-10-06", "2013-10-27", "results/event_October.pdf", "Event Detection")
}

ctrl=0
if(ctrl==2){
	makeThrashingPlot("2012-10-21", "2012-11-11", "results/events_stage1.csv", "results/events_stage2.csv", "results/events_stage3.csv", "results/thrashing.pdf")	

}

ctrl=3
if(ctrl==3){
	makeKernPlot("2012-10-21", "2012-11-11", "results/likelihood_kern.pdf", "Event Detection")
}

#makeplot("results/expected_lnl_over_time_leave1.csv", "results/expected_lnl_over_time_shrink_leave1.csv", "results/expected_likelihood_leave1.pdf", "Leave 1 Out Expected Log-Likelihood Test")



