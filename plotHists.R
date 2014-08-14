#Brian Donovan (briandonovan100@gmail.com)
#Creates histograms of trip features.  These are loaded from CSV files in hist_results/
#Also shows the error bounds for these figures, which are also defined in trip.py


#Helper function that shades the area under a curve, using a big polygon
#Arguments:
	#x - vector of x values
	#y - vector of y values
	#... - additional graphical parameters that can be passed to polygon()
shadeUnderCurve = function(x, y, ...){
  newx = c(x, rev(x))
  newy = c(y, rep(0, length(y)))
  polygon(newx, newy, ...)
  
}




#Set up PDF - 4 rows x 2 columns, small margins
pdf("results/feature_histograms.pdf", 5, 8)
par(mfrow=c(4,2), oma=c(0,0,3,0))

#All of the histogram files, corresponding titles, and corresponding colors for the plots
filenames = c('lat.csv','lon.csv','straightline.csv','dist.csv','winding.csv', 'minutes.csv','pace.csv')
titles = c('Latitude', 'Longitude', 'Straightline Distance (mi)', 'Metered Distance (mi)', 'Winding Factor', 'Duration (min)', 'Pace (min/mi)')
my_cols=c('darkred','darkred','darkblue','darkblue',rgb(.4,0,.4),'darkgreen',rgb(.3,.3,.3))

#Make each of the 7 histograms
for(i in 1:length(filenames)){

	#Load the file  
	filename = filenames[i]
	full_filename = paste("hist_results/", filenames[i], sep="")
	print(filename)
	t = read.csv(full_filename)
  

	#Depending on the feature type (indicated by filename),
	#there is an "error threshold" and a "useful threshold"
	#These are the same values that are defined in trip.py
	#camera_range determines the xlim values of the plot
	if(filename=='lat.csv'){
		s = t[t[,1] > 40.3 & t[,1] < 41.2,]
		camera_range=range(s[,1])
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
		s = t[t[,1] > -1 & t[,1] < 8000,] / 60
		camera_range=range(s[,1])
		useful=c(1, 60)
		errors=c(1/6, 120)
	}
	else if(filename=='pace.csv'){
		s = t[t[,1] > -1 & t[,1] < 6000,]/60
		camera_range=range(s[,1])
		useful=c(2/3, 60)
		errors=c(1/6, 120)
	}
	else{
		s = t
		
	}

	#Determine maximum y value
	top = max(s$frequency)

	#Create margins for this sub-graph  
	par(mar=c(2,2,2,2))
	print(camera_range)
	
	#Generate the plot and shade in the area underneath the histogram
	plot(x=s[,1], y=s$frequency, type="n", lwd=1, main=titles[i], xlim=camera_range, xlab="", ylab="", yaxt="n")
	shadeUnderCurve(x=s[,1], y=s$frequency, col=my_cols[i], border=my_cols[i])
  

	#Shade in the "not useful range"
	if(useful[2] < camera_range[2])
		rect(xleft=useful[2], xright=camera_range[2], ybottom=0, ytop=top, density=20, col="black")
	if(camera_range[1] < useful[1])
		rect(xleft=camera_range[1], xright=useful[1], ybottom=0, ytop=top, density=20, col="black")

	#Draw lines for the error thresholds
	abline(v=errors, lwd=2, lty=1)
	mtext(side=2, "Frequency", line=0.5, cex=.7)

}


#The final plot (#8) contains the legend
plot(0,0,type="n", xaxt="n", yaxt="n")
 
 
legend("center", legend=c("Uninformative Range", "Error Bounds"),
	density=c(30,NA), cex=1.3, lty=c(1,1),
	fill=c("black", rgb(0,0,0,0)),  border=c("black", rgb(0,0,0,0)),
	lwd=c(0,2),  bty="n", seg.len=c(0,2))
  
 
#Overall title for the figure
title("Data Filtering", outer=T, cex.main=2)



dev.off()
