options(width=500)

getcov = function(t, weekday, hour){
  s = t[t$Weekday==weekday & t$Hour==hour,4:ncol(t)]
  return(cov(as.matrix(s)))
}


getcor = function(t, weekday, hour){
  s = t[t$Weekday==weekday & t$Hour==hour,4:ncol(t)]
  return(cor(as.matrix(s)))
}

jet.colors =colorRamp(c("#00007F", "blue", "#007FFF", "cyan",
                     "#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))
                     
                     
plotmatrix = function(m, title){
  #layout(matrix(c(1,2),2), heights=c(10,2))
  #par(mar=c(2,3,2,.4))
  print(dim(m))
  plot(0,0,type="n",xlim=c(1,ncol(m)), ylim=c(1,nrow(m)), xlab="", ylab="", xaxt="n", yaxt="n", main=title)
  for(i in 1:nrow(m)){
    for(j in 1:ncol(m)){

	yval = nrow(m) - i + 1
	v = log(max(m[i,j],1))/log(60000)
	#print(v)
	#print(jet.colors(v))
	
	#print(rgb(jet.colors(m[i,j])/255))
	points(j, yval, col=rgb(jet.colors(v)/255), pch=15,cex=4)
	text(j, yval, round(m[i,j],2), col="black", cex=.5)
    }
   }
   abline(h=1:15+.5, lwd=1)
	abline(v=1:15+.5, lwd=1)
	
	abline(h=c(4.5,8.5,12.5),lwd=4)
	abline(v=c(4.5,8.5,12.5),lwd=4)
   axis(1,at=1:16,labels=colnames(m), cex.axis=.75)
   axis(2,at=1:16,labels=rev(rownames(m)), cex.axis=.75, las=1)
   
   #par(mar=c(2,0,.5,0))
   #plot(0,0,type="n",xlim=c(0,1), ylim=c(-1,1), xaxt="n", yaxt="n")
    #vals = seq(0, 1, length=100)
     #   mycols = rgb(jet.colors(vals)/256)
      #  yvals = rep(0,100)
	#points((1:100)/100, yvals, col=mycols, pch=15, cex=2)
	
	#a=(0:10)/10
	##print(a)
	##print(vals[a])
	#axis(1, at=a, labels=round(a, 2))
}



t = read.csv("4year_features/pace_features.csv")

weekdays =  c("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
hours = 0:23


print("********************************************* BY DAY ********************************************")
print("********************************************* BY DAY ********************************************")
print("********************************************* BY DAY ********************************************")
#z=F
#if(z==T){
#for( w in weekdays){
#  for(h in hours){
#    print(paste(w,h,":00"))
#    m = getcor(t,w,h)
#    print(m)
#    print(mean(as.vector(m)))
#    print(sd(as.vector(m)))
#  }
#}
#}

print("********************************************* BY HOUR ********************************************")
print("********************************************* BY HOUR ********************************************")
print("********************************************* BY HOUR ********************************************")
pdf("covariance_plot.pdf")
for (h in hours){
  for(w in weekdays){
    
    print(paste(w,h,":00"))
    m = getcov(t,w,h)
    print(m)
    print(mean(as.vector(m)))
    print(sd(as.vector(m)))
    title = paste("Correlation Matrix - ", w,"s ", h,":00",sep="")
    plotmatrix(m, title)
  }
}