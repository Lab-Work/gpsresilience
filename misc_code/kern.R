compareDensity = function(good_data, weekday1, hour1, weekday2, hour2, colname){
	s1 = good_data[good_data$Weekday==weekday1 & good_data$Hour==hour1,]
	s2 = good_data[good_data$Weekday==weekday2 & good_data$Hour==hour2,]
	
	print(dim(s1))
	print(dim(s2))
	
	v1 = s1[,colname]
	v2 = s2[,colname]
	
	print(dim(v1))
	print(dim(v2))
	
	d1 = density(v1, bw=10)
	d2 = density(v2, bw=10)
	
	y_rng = range(d1$y, d2$y)
	x_rng = c(0, 600)
	plot(d1, xlim =x_rng, ylim=y_rng, main=paste(colname, "Trips"), col="blue", lwd=2)
	lines(d2$x, d2$y, col="red", lwd=2)
	
	legend("topright", legend=c(paste(weekday1, hour1), paste(weekday2, hour2)), col=c("blue", "red"), lwd=2)
}







t = read.csv("../4year_features/pace_features.csv")
print(dim(t))
good_data = t[apply(t[,4:19] > 0, 1, sum) ==16,]
pdf("kern_test.pdf", 10, 10)

for(hour in 0:23){
	compareDensity(good_data, "Monday", 0, "Monday", hour, "M.M")
}



