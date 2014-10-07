t = read.csv("../results/lnl_over_time_leave1.csv")

i = 0
for(weekday in c('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')){
  for(hour in 0:23){
  	i = i + 1
  	numstring = formatC(i, width = 4, format = "d", flag = "0") 
  	filename = paste("comparisons/", numstring, ".png", sep="")
  	#png(filename, 800, 800)
    print(paste(weekday, hour))
    s = t[t$weekday==weekday & t$hour==hour,]
    plot(s$full_lnl, s$kern_lnl, main=paste("Lnl Comparison", weekday, hour),
    	xlim=quantile(s$full_lnl,c(.05, .95)), ylim=quantile(s$kern_lnl, c(.05, .95)))
    #dev.off()
  }
}
