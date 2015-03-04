error.bars<-function(x,y,stderr,length=.1,...) {
  ylim<-c(min(y-stderr),max(y+stderr))
  upy<-y+stderr
  downy<-y-stderr
  arrows(x,y,x,upy,angle=90,length=length, ...)
  arrows(x,y,x,downy,angle=90,length=length, ...)
 }




print("Loading")
t = read.csv("results/outlier_scores.csv")

png("results/error_counts.png", 32000, 300*7)

par(mfrow=c(7,1))


print("Plot 1")
filtered_p = t$mahal[t$mahal > 0]
plot(t$mahal, type="l", xaxt="n", xlab="", lwd=2, main="Mahalanobis Distance", ylim=quantile(filtered_p, c(.001, 1)))
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$date[a], las=3, cex.axis=.7)
abline(v=a)



print("Loading")
t = read.csv("4year_features/global_features.csv")

print("Plot 2")
plot(t$Pace, type="l", xaxt="n", xlab="", col="darkgreen", lwd=2, main="Pace")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$Date[a], las=3, cex.axis=.7)
abline(v=a)

print("Plot 3")
plot(t$Count, type="l", xaxt="n", xlab="", col="darkred", lwd=2, main="Trip Count")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$Date[a], las=3, cex.axis=.7)
abline(v=a)

print("Plot 4")
plot(t$Miles, type="l", xaxt="n", xlab="", col="purple", lwd=2, main="Total Miles")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$Date[a], las=3, cex.axis=.7)
abline(v=a)

print("Plot 5")
plot(t$Drivers, type="l", xaxt="n", xlab="", col="darkblue", lwd=2, main="Total Unique Drivers")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$Date[a], las=3, cex.axis=.7)
abline(v=a)


print("Plot 6")

bad_data = t$BAD_GPS + t$BAD_LO_STRAIGHTLINE + t$BAD_HI_STRAIGHTLINE + t$BAD_LO_DIST + t$BAD_HI_DIST + t$BAD_LO_WIND + t$BAD_HI_WIND + t$BAD_LO_TIME + t$BAD_HI_TIME + t$BAD_LO_PACE + t$BAD_HI_PACE


err_data = t$ERR_GPS + t$ERR_LO_STRAIGHTLINE + t$ERR_HI_STRAIGHTLINE + t$ERR_LO_DIST +
            t$ERR_HI_DIST + t$ERR_LO_WIND + t$ERR_HI_WIND + t$ERR_LO_TIME +
            t$ERR_HI_TIME + t$ERR_LO_PACE + t$ERR_HI_PACE + t$ERR_OTHER

err_date_data = t$ERR_DATE



errs = bad_data + err_data + err_date_data
totals = errs + t$VALID


p_errs = errs / (errs + totals)

plot(p_errs, type="l", xaxt="n", xlab="", col="black", lwd=2, main="Total Errors")
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$Date[a], las=3, cex.axis=.7)
abline(v=a)


print("Plot 7")
plot(t$AvgWind, type="l", xaxt="n", xlab="", col="red", lwd=2, main="Winding Factor", ylim=range(t$AvgWind - t$SdWind, t$AvgWind + t$SdWind))
error.bars(1:nrow(t), t$AvgWind, t$SdWind, col="red", lwd=1)
a = seq(1,nrow(t),24)
axis(1,at=a, labels=t$Date[a], las=3, cex.axis=.7, length=.1)
abline(v=a)







dev.off()
