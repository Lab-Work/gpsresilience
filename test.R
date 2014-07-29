error.bars<-function(x,y,stderr,length=.1,...) {
  ylim<-c(min(y-stderr),max(y+stderr))
  upy<-y+stderr
  downy<-y-stderr
  arrows(x,y,x,upy,angle=90,length=length, ...)
  arrows(x,y,x,downy,angle=90,length=length, ...)
 }




print("Loading")
t = read.csv("results/lnl_over_time_leave1.csv")

png("tmp.png", 32000*5, 200*7)

par(mfrow=c(1,1))


print("Plot 1")
filtered_p = t$full_lnl[t$full_lnl < 0]
plot(t$full_lnl, type="l", xaxt="n", xlab="", lwd=2, main="Log-Probability", ylim=quantile(filtered_p, c(.001, 1)))
abline(h=quantile(filtered_p, c(.1,.05,.01)), col="red")
lines(t$ind_lnl, col="blue")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$date[a], las=3, cex.axis=.7)
abline(v=a)
dev.off()
q()

print("Loading")
t = read.csv("4year_features/global_features.csv")

print("Plot 2")
plot(t$Pace, type="l", xaxt="n", xlab="", col="darkgreen", lwd=2, main="Pace")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$date[a], las=3, cex.axis=.7)
abline(v=a)

print("Plot 3")
plot(t$Count, type="l", xaxt="n", xlab="", col="darkred", lwd=2, main="Trip Count")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$date[a], las=3, cex.axis=.7)
abline(v=a)

print("Plot 4")
plot(t$Miles, type="l", xaxt="n", xlab="", col="purple", lwd=2, main="Total Miles")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$date[a], las=3, cex.axis=.7)
abline(v=a)

print("Plot 5")
plot(t$Drivers, type="l", xaxt="n", xlab="", col="darkblue", lwd=2, main="Total Unique Drivers")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$date[a], las=3, cex.axis=.7)
abline(v=a)


print("Plot 6")
errs = t$err_gps + t$err_straightline + t$err_duration + t$err_dist + t$err_pace + t$err_winding + t$err_other
p_errs = errs / (errs + t$Count)
plot(p_errs, type="l", xaxt="n", xlab="", col="black", lwd=2, main="Total Errors")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$date[a], las=3, cex.axis=.7)
abline(v=a)


print("Plot 7")
plot(t$AvgWind, type="l", xaxt="n", xlab="", col="red", lwd=2, main="Winding Factor")
error.bars(1:nrow(t), t$AvgWind, t$SdWind, col="red", lwd=1)
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$date[a], las=3, cex.axis=.7, length=.1)
abline(v=a)







dev.off()