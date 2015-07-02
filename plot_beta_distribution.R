


x = seq(0,1,.005)

y1 = dbeta(x,9.9,.1)  # a,b
y2 = dbeta(x,17.1,.9) # c
y3 = dbeta(x,57,38)   # d

yl = range(y1,y2,y3)

pdf("beta_distributions.pdf",10,5)
plot(x,y1, col="black", type="l", lwd=2, xlab="Parameter Value", ylab="PDF", main="Parameter Distributions for HMM Sensitivity Analysis")
lines(x,y2, col="red", lwd=2)
lines(x,y3, col="blue", lwd=2)

legend("topleft", legend=c('a, b', 'c', 'd'), col=c('black','red','blue'), lwd=2)
dev.off()
