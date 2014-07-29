PACE_RANGE=c(0,600)
t = read.csv("4year_features/pace_features.csv")
t$Date = as.character(t$Date)

print(dim(t))

plotDay = function(date, hour, showObs){
    par(mfrow=c(4,4), mar=c(2,.5,.5,.5))
    weekday = t$Weekday[t$Date==date][1]
    print(weekday)
    s = t[t$Weekday==weekday & t$Hour==hour,]
    
    print(dim(s))
    mynames = c("a","a","a","E -> E", "E -> U", "E -> M", "E -> L",
			    "U -> E", "U -> U", "U -> M", "U -> L",
			    "M -> E", "M -> U", "M -> M", "M -> L",
			    "L -> E", "L -> U", "L -> M", "L -> L")

    for(colid in 4:ncol(s)){
      mu = mean(s[,colid])
      sig = sd(s[,colid])
      
      obs = s[s$Date==date & s$Hour==hour,colid]
      
      #print(mu)
      #print(sig)
      
      print(obs)
      x = seq(PACE_RANGE[1],PACE_RANGE[2])
      y = dnorm(x, mu, sig)
      
      plot(0,0,type="n", xlim=PACE_RANGE, ylim=range(y), yaxt="n")
    
      

	my_x = c(x, rev(x))
	my_y = c(y, rep(0, length(x)))
	polygon(my_x, my_y, col="grey")
      
      if(showObs){
	if(obs >= mu){
	  x_rel = x[x>=obs]
	  y_rel = y[x>=obs]
	}
	else{
	  x_rel = x[x<obs]
	  y_rel = y[x<obs]
	}
	
	my_x = c(x_rel, rev(x_rel))
	my_y = c(y_rel, rep(0, length(x_rel)))
	polygon(my_x, my_y, col="blue")
      
	abline(v=obs, col="red", lwd=2)
      
      
      
      }
      
      text(mean(PACE_RANGE), max(y)/2, mynames[colid], cex=2)
    
    }
    

}

svg("results/city_wed_7.svg", 6, 4)
plotDay("2013-03-13", 7, FALSE)
dev.off()

svg("results/city_2013_03_13.svg", 6, 4)
plotDay("2013-03-13", 7, TRUE)
dev.off()

svg("results/city_2012_10_31.svg", 6, 4)
plotDay("2012-10-31", 7, TRUE)
dev.off()








