t = read.csv("features/pace_features.csv")

#remove outliers
n = t[t$E.E< 1000 & t$E.U< 1000 & t$E.M< 1000 & t$E.L< 1000 & t$U.E< 1000 & t$U.U< 1000 & t$U.M< 1000 & t$U.L< 1000 & t$M.E< 1000 & t$M.U< 1000 & t$M.M< 1000 & t$M.L< 1000 & t$L.E< 1000 & t$L.U< 1000 & t$L.M< 1000 & t$L.L< 1000,]



pdf("pace_hist.pdf", 20, 20)
par(mfrow=c(4,4))
hist(n$E.E, main="all", breaks=20)
hist(n$E.U, breaks=20)
hist(n$E.M, breaks=20)
hist(n$E.L, breaks=20)

hist(n$U.E, breaks=20)
hist(n$U.U, breaks=20)
hist(n$U.M, breaks=20)
hist(n$U.L, breaks=20)

hist(n$M.E, breaks=20)
hist(n$M.U, breaks=20)
hist(n$M.M, breaks=20)
hist(n$M.L, breaks=20)

hist(n$L.E, breaks=20)
hist(n$L.U, breaks=20)
hist(n$L.M, breaks=20)
hist(n$L.L, breaks=20)


print(summary(n$Hour))

day = n[n$Hour>6 & n$Hour < 19,]
night = n[!(n$Hour>6 & n$Hour < 19),]

print(dim(day))
print(range(day$Hour))
par(mfrow=c(4,4))
hist(day$E.E, main="day", breaks=20)
hist(day$E.U, breaks=20)
hist(day$E.M, breaks=20)
hist(day$E.L, breaks=20)

hist(day$U.E, breaks=20)
hist(day$U.U, breaks=20)
hist(day$U.M, breaks=20)
hist(day$U.L, breaks=20)

hist(day$M.E, breaks=20)
hist(day$M.U, breaks=20)
hist(day$M.M, breaks=20)
hist(day$M.L, breaks=20)

hist(day$L.E, breaks=20)
hist(day$L.U, breaks=20)
hist(day$L.M, breaks=20)
hist(day$L.L, breaks=20)



print(dim(night))
print(range(night$Hour))
par(mfrow=c(4,4))
hist(night$E.E, main="night", breaks=20)
hist(night$E.U, breaks=20)
hist(night$E.M, breaks=20)
hist(night$E.L, breaks=20)

hist(night$U.E, breaks=20)
hist(night$U.U, breaks=20)
hist(night$U.M, breaks=20)
hist(night$U.L, breaks=20)

hist(night$M.E, breaks=20)
hist(night$M.U, breaks=20)
hist(night$M.M, breaks=20)
hist(night$M.L, breaks=20)

hist(night$L.E, breaks=20)
hist(night$L.U, breaks=20)
hist(night$L.M, breaks=20)
hist(night$L.L, breaks=20)




dev.off()



pdf("distributions/lnl.pdf", 200, 5)

t_n = read.csv("distributions/normal.csv")
plot(0,0,type="n",xlim=c(1,nrow(t_n)), ylim=range(t_n$E.E), main="Normal")
for(i in 4:ncol(t_n)){
  lines(t_n[,i],col=i)
}

t_n = read.csv("distributions/normal_1tail.csv")
plot(0,0,type="n",xlim=c(1,nrow(t_n)), ylim=range(t_n$E.E), main="Normal 1 tail")
for(i in 4:ncol(t_n)){
  lines(t_n[,i],col=i)
}



t_ln = read.csv("distributions/lognormal.csv")
plot(0,0,type="n",xlim=c(1,nrow(t_ln)), ylim=range(t_ln$E.E), main="LogNormal")
for(i in 4:ncol(t_ln)){
  lines(t_ln[,i],col=i)
}

t_k = read.csv("distributions/kernel.csv")
plot(0,0,type="n",xlim=c(1,nrow(t_ln)), ylim=range(t_k$E.E), main="Kernel")
for(i in 4:ncol(t_k)){
  lines(t_k[,i],col=i)
}

dev.off()



pdf("distributions/compare_times2.pdf", 10, 80)

par(mfrow=c(24,1))
for(i in 0:23){
  samp = t$E.M[t$Weekday=="Friday" & t$Hour ==i]
 
  d = density(samp)
  
  plot(d,new=T, main=paste("Midtown to Midtown Trips - Wednesdays at ",i, ":00"), xlim=c(0,1200), lwd=2, xlab="Pace")
  #points(x=samp, y=rnorm(length(samp))/1000 + .01, pch=19,cex=2)
  points(x=samp,y=rep(0,length(samp)),pch=19,cex=.5)
  
  
  
  my_x = seq(0,1200,length=1200)
  my_y = dnorm(my_x, mean=mean(samp), sd=sd(samp))
  lines(my_x,my_y,col="red")
  
  
  trimmed = samp[samp >=quantile(samp,.01) & samp <= quantile(samp, .99)]
  print(length(samp))
  print(length(trimmed))
  print("*********")
  
  my_x = seq(0,1200,length=1200)
  my_y = dnorm(my_x, mean=mean(trimmed), sd=sd(trimmed))
  lines(my_x,my_y,col="blue")
  
  legend("topright", legend=c("Kernel Density Estimate", "Normal Density (Fitted to all data)", "Normal Density (Fitted to trimmed data)"),
  lty=)
  
}
dev.off()

