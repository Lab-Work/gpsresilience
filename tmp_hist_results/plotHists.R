shadeUnderCurve = function(x, y, ...){
  newx = c(x, rev(x))
  newy = c(y, rep(0, length(y)))
  polygon(newx, newy, ...)
  
}








pdf("feature_histograms.pdf", 5, 8)
par(mfrow=c(4,2), oma=c(0,0,3,0))

filenames = c('lat.csv','lon.csv','straightline.csv','dist.csv','winding.csv', 'minutes.csv','pace.csv')
titles = c('Latitude', 'Longitude', 'Straightline Distance (mi)', 'Metered Distance (mi)', 'Winding Factor', 'Duration (min)', 'Pace (min/mi)')

my_cols=c('darkred','darkred','darkblue','darkblue',rgb(.4,0,.4),'darkgreen',rgb(.3,.3,.3))

for(i in 1:length(filenames)){
  
  filename = filenames[i]

  t = read.csv(filename)
  

  if(filename=='lat.csv'){
    s = t[t[,1] > 40.3 & t[,1] < 41.2,]
    camera_range=range(s[,1])
    useful=c(40.65,40.9)
    errors=c(40.4, 41.1)
  }
  else if(filename=='lon.csv'){
    s = t[t[,1] > -74.3 & t[,1] < -73.5,]
    camera_range=c(-74.3, -73.5)
    useful=c(-74.05, -73.85)
    errors=c(-74.25, -73.5)
  }
  else if(filename=='straightline.csv'){
    s = t[t[,1] > -1 & t[,1] < 10,]
    camera_range=range(s[,1])
    useful=c(0, 8)
    errors=c(0, 20)
  }
  else if(filename=='dist.csv'){
    s = t[t[,1] > -1 & t[,1] < 20,]
    camera_range=range(s[,1])
    useful=c(0, 15)
    errors=c(0, 20)
  }
  else if(filename=='miles.csv'){
    s = t[t[,1] > -1 & t[,1] < 20,]
    camera_range=range(s[,1])
    useful=c(.5, 15)
    errors=c(.1, 20)
  }
  else if(filename=='winding.csv'){
    s = t[t[,1] > -1 & t[,1] < 6,]
    camera_range=range(s[,1])
    useful=c(.95,5)
    errors=c(.95, 10000)
  }
  else if(filename=='time.csv'){
    s = t[t[,1] > -1 & t[,1] < 5000,] / 60
    camera_range=range(s[,1])
    useful=c(1, 60)
    errors=c(1/6, 120)
  }
  else if(filename=='minutes.csv'){
    t[,1] = t[,1] / 60
    s = t[t[,1] > -1 & t[,1] < 80,]
    camera_range=range(s[,1])
    useful=c(1, 60)
    errors=c(1/6, 120)
  }
  else if(filename=='pace.csv'){
    t[,1] = t[,1] / 60
    s = t[t[,1] > -1 & t[,1] < 80,]
    #s = t[t[,1] > -1 & t[,1] < 120,]
    camera_range=range(s[,1])
    useful=c(2/3, 60)
    errors=c(1/6, 120)
  }
  else{
    s = t
  }


  error_points = (t[,1] < useful[1] | t[,1] > useful[2])



  num_errors = sum(t$frequency[error_points])
  perc_errors = round(num_errors / sum(t$frequency)*100, digits=2)
  print(paste(filename, useful[1], useful[2], perc_errors, sep=", "))


  top = max(s$frequency)
  
  par(mar=c(2,2,2,2))

  plot(x=s[,1], y=s$frequency, type="n", lwd=1, main=titles[i], xlim=camera_range, xlab="", ylab="", yaxt="n")
  shadeUnderCurve(x=s[,1], y=s$frequency, col=my_cols[i], border=my_cols[i])
  

	if(useful[2] < camera_range[2])
		rect(xleft=useful[2], xright=camera_range[2], ybottom=0, ytop=top, density=20, col="black", lwd=1.5)
	if(camera_range[1] < useful[1])
		rect(xleft=camera_range[1], xright=useful[1], ybottom=0, ytop=top, density=20, col="black", lwd=1.5)


	mtext(side=2, "Frequency", line=0.5, cex=.7)

}

#plot(0,0,type="n", xaxt="n", yaxt="n")
plot(0,0,type="n", xaxt="n", yaxt="n")
 
 
  legend("center", legend=c("Error Bounds"),
	density=30, cex=1.3, lty=1,
	fill="black",  border=c("black"),
	lwd=0,  bty="n", seg.len=0)
  
 
 title("Error Filtering", outer=T, cex.main=1.2)



dev.off()
