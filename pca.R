removeRowsWithZeros= function(t){
	z = (t==0) + 0 #Z is a matrix of the same dimension of t.  It contains a 1 where t==0, and a 0 everywhere else
	numZeros = rowSums(z) #Sum each row (count the number of 0s)
	goodRows = (numZeros == 0) #Bad rows have at least one 0
	return (t[goodRows,])	#Perform the selection
}




mydata = read.csv("4year_features/pace_features.csv")
y <- as.matrix(mydata[,4:ncol(mydata)]) # select vars for matrix

print("Making original pairs scatterplot")
png("results/original_pairs.png", 5000,5000)
pairs(y, pch=20, cex=.1)
dev.off()

print(dim(y))
y = removeRowsWithZeros(y)
print(dim(y))

y <- t(scale(t(y),scale=FALSE)) # center rows



v = cov(y) #compute the covariance matrix of the data
eig = eigen(v) #decompose cov matrix

rotated_data = y %*% eig$vectors #transform data

print("Making princomp scatterplot")
png("results/pca_pairs.png", 5000, 5000)
pairs(rotated_data, pch=20, cex=.1)
dev.off()

################################################################################################################################################

print("Making biplot")
png("results/PCA_biplot.png", 1000, 1000)
#Plot the data, projected onto the
#first two eigenvectors
#We will assume that the first eigenvector
#is X, and the second is Yas
#(the remaining columns are ignored)
plot(rotated_data[,1], rotated_data[,2], xlab="PC1", ylab="PC2", pch=20, cex=.5)




#Plot the original coordinate projected onto the
#first two eigenvectors.  The rows of eig$vectors are
#the projected data-we only need the first two entries
#from each row
SCALING_FACTOR = 800 #Influences the size of arrows
ax_x = eig$vectors[,1]*SCALING_FACTOR
ax_y = eig$vectors[,2]*SCALING_FACTOR

cx = mean(range(rotated_data[,1]))
cy = mean(range(rotated_data[,2]))
arrows(cx, cy, cx+ax_x, cy + ax_y, col="blue", lwd=3)
#Add labels to the arrows
text(cx+ax_x, cy + ax_y, labels=names(y[1,]), col="red", cex=2)
dev.off()

################################################################################################################################################


jet.colors = colorRampPalette(c("#00007F","blue", "#007FFF", "cyan", "#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))


print("Making smooth biplot")
png("results/PCA_smooth_biplot.png", 1000, 1000)
#Plot the data, projected onto the
#first two eigenvectors
#We will assume that the first eigenvector
#is X, and the second is Yas
#(the remaining columns are ignored)
smoothScatter(rotated_data[,1], rotated_data[,2], xlab="PC1", ylab="PC2", colramp=jet.colors)




#Plot the original coordinate projected onto the
#first two eigenvectors.  The rows of eig$vectors are
#the projected data-we only need the first two entries
#from each row
SCALING_FACTOR = 800 #Influences the size of arrows
ax_x = eig$vectors[,1]*SCALING_FACTOR
ax_y = eig$vectors[,2]*SCALING_FACTOR

cx = mean(range(rotated_data[,1]))
cy = mean(range(rotated_data[,2]))
arrows(cx, cy, cx+ax_x, cy + ax_y, col="green", lwd=3)
#Add labels to the arrows
text(cx+ax_x, cy + ax_y, labels=names(y[1,]), col="black", cex=2)
dev.off()


################################################################################################################################################

print("Plotting eigenvalues")
pdf("results/PCA_eigenvalues.pdf")
barplot(eig$values, main="Eigenvalues", ylab="Variance")
plot(cumsum(eig$values)/sum(eig$values), main="Portion of Variance from top N PCs", type="l", lwd=2)
points(cumsum(eig$values)/sum(eig$values))

dev.off()






