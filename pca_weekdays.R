mydata = read.csv("4year_features/pace_features.csv")

removeRowsWithZeros= function(t){
	z = (t==0) + 0 #Z is a matrix of the same dimension of t.  It contains a 1 where t==0, and a 0 everywhere else
	numZeros = rowSums(z) #Sum each row (count the number of 0s)
	goodRows = (numZeros == 0) #Bad rows have at least one 0
	return (t[goodRows,])	#Perform the selection
}

makeplot = function(weekday, hour){
	print(paste(weekday, hour))
	s = mydata[mydata$Weekday == weekday & mydata$Hour ==hour,]
	y <- as.matrix(s[,4:ncol(mydata)]) # select vars for matrix

	y = removeRowsWithZeros(y)


	y <- t(scale(t(y),scale=FALSE)) # center rows

	v = cov(y) #compute the covariance matrix of the data
	eig = eigen(v) #decompose cov matrix
	
	rotated_data = y %*% eig$vectors #transform data

	par(mfrow=c(1,2))
	#Plot the data, projected onto the
	#first two eigenvectors
	#We will assume that the first eigenvector
	#is X, and the second is Yas
	#(the remaining columns are ignored)
	mytitle = paste("PCA - ", weekday, "  ", hour, ":00", sep="")
	plot(rotated_data[,1], rotated_data[,2], xlab="PC1", ylab="PC2", pch=20, cex=.5, main=mytitle)
	#Plot the original coordinate projected onto the
	#first two eigenvectors.  The rows of eig$vectors are
	#the projected data-we only need the first two entries
	#from each row

	#SCALING_FACTOR = 800 #Influences the size of arrows
	xrng = range(rotated_data[,1])
	yrng = range(rotated_data[,2])
	minsize = min(xrng[2] - xrng[1], yrng[2] - yrng[1]) / 2
	print(minsize)
	print(eig$values)
	SCALING_FACTOR = minsize * .8
	print(SCALING_FACTOR)




	ax_x = eig$vectors[,1]*SCALING_FACTOR
	ax_y = eig$vectors[,2]*SCALING_FACTOR

	cx = mean(range(rotated_data[,1]))
	cy = mean(range(rotated_data[,2]))
	segments(cx, cy, cx+ax_x, cy + ax_y, col="blue", lwd=1.5)
	#Add labels to the arrows
	text(cx+ax_x, cy + ax_y, labels=names(y[1,]), col="red", cex=.9)


	barplot(eig$values, main="Eigenvalues", ylab="Variance")

}

pdf("results/pca_weekdays.pdf", 10, 5)
hours = 0:23
weekdays = c("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

for(w in weekdays){
	for(h in hours){
		makeplot(w, h)
	}
}

dev.off()



