shadeUnderCurve = function(x, y, ...){
  newx = c(x, rev(x))
  newy = c(y, rep(0, length(y)))
  polygon(newx, newy, ...)
  
}



svg("feature_histograms2.svg", 8, 6)
par(mfrow=c(2,4), oma=c(0,0,3,0))

filenames = c('lat.csv','lon.csv','straightline.csv','dist.csv','winding.csv', 'minutes.csv','pace.csv')
titles = c('Latitude', 'Longitude', 'Straightline Distance (mi)', 'Distance (mi)', 'Winding Factor', 'Time (s)', 'Pace (s/mi)')

my_cols=c('darkred','darkred','darkblue','darkblue',rgb(.4,0,.4),'darkgreen',rgb(.3,.3,.3))

for(i in 1:length(filenames)){
  
  filename = filenames[i]
  print(filename)
  t = read.csv(filename)
  
  camera_range=NULL
  if(filename=='lat.csv'){
    s = t[t[,1] > 40.3 & t[,1] < 41.2,]
    useful=c(40.6,40.9)
    errors=c(40.4, 41.1)
  }
  else if(filename=='lon.csv'){
    s = t[t[,1] > -74.3 & t[,1] < -73.5,]
    camera_range=c(-74.3, -73.5)
    useful=c(-74.05, -73.7)
    errors=c(-74.25, -73.5)
  }
  else if(filename=='straightline.csv'){
    s = t[t[,1] > -1 & t[,1] < 10,]
    useful=c(.5, 8)
    errors=c(.01, 20)
  }
  else if(filename=='dist.csv'){
    s = t[t[,1] > -1 & t[,1] < 20,]
    useful=c(.5, 15)
    errors=c(.01, 20)
  }
  else if(filename=='miles.csv'){
    s = t[t[,1] > -1 & t[,1] < 20,]
    useful=c(.5, 15)
    errors=c(.1, 20)
  }
  else if(filename=='winding.csv'){
    s = t[t[,1] > -1 & t[,1] < 6,]
    useful=c(.95,5)
    errors=c(.95, 10000)
  }
  else if(filename=='time.csv'){
    s = t[t[,1] > -1 & t[,1] < 5000,]
    useful=c(60, 3600)
    errors=c(10, 7200)
  }
  else if(filename=='minutes.csv'){
    s = t[t[,1] > -1 & t[,1] < 8000,]
    useful=c(60, 3600)
    errors=c(10, 7200)
  }
  else if(filename=='pace.csv'){
    s = t[t[,1] > -1 & t[,1] < 6000,]
    #s = t[t[,1] > -1 & t[,1] < 120,]
    
    useful=c(40, 3600)
    errors=c(10, 7200)
  }
  else{
    s = t
  }

  
  
  par(mar=c(2,2,2,2))
  print(camera_range)
  plot(x=s[,1], y=s$frequency, type="n", lwd=1, main=titles[i], xlim=camera_range, xlab="", ylab="", yaxt="n")
  shadeUnderCurve(x=s[,1], y=s$frequency, col=my_cols[i], border=my_cols[i])
  
  abline(v=useful, lwd=3, lty=2)
  abline(v=errors, lwd=2, lty=1)

}

#plot(0,0,type="n", xaxt="n", yaxt="n")
plot(0,0,type="n", xaxt="n", yaxt="n")
 
 
  legend("center", legend=c("Useful Range", "Error Range"), lwd=c(2,2), lty=c(2,1), bg="white", cex=1.4, bty="n")
 
 title("Error Filtering", outer=T, cex.main=2)



dev.off()