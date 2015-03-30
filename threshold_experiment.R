t = read.csv("results/threshold_experiment.csv")


pdf("results/threshold_experiment.pdf")

plot(0,0,type="n",xlim=c(.9,1), ylim=c(0,350), main="Comparison of Event Dection Parameters\n(Threshold and Window Size)",
	xlab="Threshold (Mahalanobis Quantile)", ylab="Hurricane Sandy Duration (hours)")
i=0
for(w in c(1,2,3,4,6,8,12,24)){
	s = t[t$granularity=='coarse' & t$window==w,]
	lines(s$threshold, s$duration, col="black")
	if(i %% 2==0){
		mythresh=.91
	}else{
		mythresh=.92	
	}

	text(x=mythresh, s$duration[s$threshold==mythresh], paste("w=",w,sep=""), col="black")


	s = t[t$granularity=='fine' & t$window==w,]
	lines(s$threshold, s$duration, col="blue")
	text(x=mythresh, s$duration[s$threshold==mythresh], paste("w=",w,sep=""), col="blue")
	i = i + 1
}

dev.off()
