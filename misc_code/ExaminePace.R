error.bars = function(x, sdev, ...){
  arrows(x0=1:length(x), x1=1:length(x), y0=x-sdev, y1=x+sdev, code=3,angle=90, length=.03, ...)
}



t = read.csv("4year_features/pace_features.csv")

t$Date = as.character(t$Date)

s = t[t$Date>="2013-04-07" & t$Date<="2013-04-28",]

daynames = c("Su", "M", "Tu", "W", "Th", "F", "Sa")


svg("test.svg", 12,4)
plot(s$M.M, type="l", xaxt="n", ylab="Pace", lwd=2, col="blue", main="Midtown to Midtown Trips", xlab="")

a = (0:20)*24 + 1


axis(1, labels=rep(daynames,3), at=a)
abline(v=a)

dev.off()

fulldaynames = c("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
hours = 0:23

mylabs = character(7*24)
avg = numeric(7*24)
sdev = numeric(7*24)

i = 1
for(day in fulldaynames){
  for(h in hours){
    s = t[t$Weekday==day & t$Hour==h,]
    print(dim(s))
    
    j = which(fulldaynames==day)
    mylabs[i] = paste(daynames[j], h, ":00")
    avg[i] = mean(s$M.M)
    sdev[i] = sd(s$M.M)
    
    i = i + 1
  }
}

svg("test2.svg", 12, 4)
a = (0:(4*7))*6 + 1

plot(avg, type="l", col="red", lwd=2, xaxt="n", ylab="Pace", xlab="", ylim=c(100,700), main="Average Week - Midtown to Midtown Trips")
axis(1, labels=mylabs[a], at=a, las=3)
error.bars(avg, sdev, col="red", lwd=1)
dev.off()



svg("test3.svg", 12, 8)
s = t[t$Weekday=="Wednesday" & t$Hour==7,]
d = density(s$M.M)
plot(d, new=T, main=paste("Midtown to Midtown Trips - Wednesdays at 7am"), lwd=2, xlab="Probability Density")
yvals = rnorm(nrow(s))*.001 + .002
points(x=s$M.M,y=yvals,pch=19,cex=.5)


my_x = seq(0,1200,length=1200)
my_y = dnorm(my_x, mean=mean(s$M.M), sd=sd(s$M.M))
lines(my_x,my_y,col="red", lwd=2)

legend("topright", legend=c("Kernel Density Estimate", "Normal Density Estimate"),lty=1, col=c("black", "red"), lwd=2)
  

dev.off()