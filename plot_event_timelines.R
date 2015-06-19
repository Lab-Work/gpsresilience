k_vals = 7:50
#k_vals = 7:10
tabs = list()

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



for(k in k_vals){
	print(paste("reading",k))
	filename = paste('results/coarse_events_k',k,'_scores.csv', sep='')
	tabs[[k]] = read.csv(filename)
	tabs[[k]]$date = as.character(tabs[[k]]$date)
}

plot_time_range = function(start_date, end_date, title){
	print(paste('plotting', title))
	
	t = tabs[[k_vals[1]]]
	

	s = t[t$date >= start_date & t$date <= end_date,]
	perc_outliers = rep(0, nrow(s))
	layout(matrix(c(1,2), 2, 1, byrow = TRUE), heights=c(3,1))
	par(mar=c(2,4,2,1))
	plot(0,0,type='n', xlim=c(0,nrow(s)), ylim=c(0,max(k_vals)), main=title, xaxt='n', xlab='Date', ylab='Number of Regions')
		
	print("b")

	a = seq(1,nrow(s),24)
	axis(1,labels=s$date[a], at=a)
	
	for(k in k_vals){
		t = tabs[[k]]
		s = t[t$date >= start_date & t$date <= end_date,]
		cols = ifelse(s$state==1, 'black', 'white')
		y_vals=rep(k,nrow(s))
		points(1:nrow(s),y_vals,col=cols,pch=15, cex=.6)
		
		thresh = quantile(t$mahal10, .95)	
		outliers = (s$c_val==1 | s$mahal10 > thresh)
		perc_outliers = perc_outliers + outliers
		cols = ifelse(outliers, 'red', 'white')
		points(1:nrow(s),y_vals,col=cols,pch=20,cex=.2)
	}
	print("c")
	perc_outliers = perc_outliers / length(k_vals)
	abline(v=a)
	legend("bottomright", legend=c("Outlier", "Event"), col=c("red", "black"), pch=c(20,15),  bg="white")
	
	
	plot(perc_outliers, type="l", xaxt="n", xlab="Date", ylab="Perc Outliers", yaxt="n", ylim=c(0,1))
	axis(1,labels=s$date[a], at=a)
	axis(2,at=c(0,.5,1))
	abline(v=a)
	print("d")
}


get_consensus = function(){
	t = tabs[[k_vals[1]]]
	avg_outliers = rep(0, nrow(t))
	for(k in k_vals){
		t = tabs[[k]]
		thresh = quantile(t$mahal10, .95)	
		outliers = (t$c_val==1 | t$mahal10 > thresh)
		avg_outliers = avg_outliers + outliers
	}
	avg_outliers = avg_outliers / length(k_vals)
	consensus = avg_outliers > .5
	return(consensus)
}


plot_consensus = function(consensus){
	false_pos = rep(0, length(k_vals))
	false_neg = rep(0, length(k_vals))
	for(i in 1:length(k_vals)){
		k = k_vals[i]
		t = tabs[[k]]
		thresh = quantile(t$mahal10, .95)	
		outliers = (t$c_val==1 | t$mahal10 > thresh)
		false_pos[i] = sum(outliers & !consensus) / sum(!consensus)
		false_neg[i] = sum(!outliers & consensus) / sum(consensus)
	}

	plot(k_vals,false_pos, type="l", ylim=c(0,.4), col="black", lwd=2, xlab="Number of Regions", ylab="Error", main="Outlier Consensus with Different Regions")
	lines(k_vals,false_neg, col="red", lwd=2)
	legend("topright", legend=c("False Positives", "False Negatives"), col=c("black", "red"), lwd=2)

	plot(k_vals,false_pos, type="l", ylim=c(0,.04), col="black", lwd=2, xlab="Number of Regions", ylab="Error", main="Outlier Consensus with Different Regions")
	lines(k_vals,false_neg, col="red", lwd=2)
	legend("topright", legend=c("False Positives", "False Negatives"), col=c("black", "red"), lwd=2)
}



add_legend=function(lo,hi,value_granularity, legend_granularity, title){
	vals = seq(lo, hi, 1/value_granularity)
	cvals = linearScale(vals, lo, hi)
	mycols = rgb(jet.colors(cvals)/255)
	a = c((0:((hi - lo)/legend_granularity))*value_granularity*legend_granularity + 1)
	print(vals)
	print(a)

	par(mar=c(.1,0,1,0))
        plot(0,0, type="n", xlim=c(lo,hi), ylim=c(0,1), xaxt="n", yaxt="n", , bty="n", cex.main=1, main=title)
        #y is constant
        yvals = rep(.6,length(vals))
        
        #Draw the squares
	points(vals, yvals, col=mycols, pch=15, cex=2)
	

	#Add the ticks and axis labels
	segments(x0=vals[a],y0=.4,x1=vals[a],y1=.8, lwd=2)
	text(x=vals[a],y=.2,labels=vals[a], cex=.8)
}



plot_pairwise_consensus = function(){
	############# FALSE POSITIVES
	par(mar=c(5.1,4.1,4.1,2.1))
	layout(matrix(c(1,2),2), heights=c(10,2))
	plot(0,0,type="n", xlim=range(k_vals), ylim=range(k_vals), xlab="Ground Truth Num Regions", ylab="Compared Num Regions")
	for(i in k_vals){
		print(i)
		t = tabs[[i]]
		thresh = quantile(t$mahal10, .95)
		gt_outliers = (t$c_val==1 | t$mahal10 > thresh)
		for(j in k_vals){
			t = tabs[[j]]
			thresh = quantile(t$mahal10, .95)
			ex_outliers = (t$c_val==1 | t$mahal10 > thresh)

			false_pos = sum(ex_outliers & !gt_outliers) / sum(!gt_outliers)
			false_pos = linearScale(false_pos, 0,.1)
			
			col = rgb(jet.colors(false_pos)/255)
			points(i,j, col=col, pch=15, cex=2)

		}
	}

	add_legend(0,.1,1000,.01, "False Positives")

	################ FALSE NEGATIVES
	par(mar=c(5.1,4.1,4.1,2.1))
	layout(matrix(c(1,2),2), heights=c(10,2))
	plot(0,0,type="n", xlim=range(k_vals), ylim=range(k_vals), xlab="Ground Truth Num Regions", ylab="Compared Num Regions")
	for(i in k_vals){
		print(i)
		t = tabs[[i]]
		thresh = quantile(t$mahal10, .95)
		gt_outliers = (t$c_val==1 | t$mahal10 > thresh)
		for(j in k_vals){
			t = tabs[[j]]
			thresh = quantile(t$mahal10, .95)
			ex_outliers = (t$c_val==1 | t$mahal10 > thresh)

			false_neg = sum(!ex_outliers & gt_outliers) / sum(gt_outliers)
			false_neg = linearScale(false_neg, 0,1)
			
			col = rgb(jet.colors(false_neg)/255)
			points(i,j, col=col, pch=15, cex=2)

		}
	}

	add_legend(0,1,100,.1, "False Negatives")
}


pdf('results/typical_timeline.pdf')
plot_time_range('2012-04-08', '2012-04-15', 'Typical Week 1')
plot_time_range('2012-04-15', '2012-04-22', 'Typical Week 2')
plot_time_range('2012-04-22', '2012-04-28', 'Typical Week 3')
dev.off()


pdf('results/event_parwise_consensus.pdf')
plot_pairwise_consensus()
dev.off()



pdf('results/event_timelines.pdf')

plot_time_range('2010-12-26', '2011-01-05', 'Snowstorm')
plot_time_range('2012-10-28', '2012-11-05', 'Sandy')
plot_time_range('2012-11-12', '2012-11-19', '?')
plot_time_range('2011-01-25', '2011-02-08', 'Snowstorm(s)')
plot_time_range('2011-09-15', '2011-09-24', 'Protest?')
plot_time_range('2011-08-27', '2011-09-07', 'Irene')

dev.off()



pdf('results/event_consensus.pdf')
consensus = get_consensus()
print(consensus)
print(sum(consensus) / length(consensus))
plot_consensus(consensus)
dev.off()

