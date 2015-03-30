t = read.csv("results/link_50_normalize_zscore.csv")

t$Date = as.character(t$Date)

#smallz = t[18067:(18067+168*40) , 4:ncol(t)]
smallz = t[t$Date>='2012-10-21' & t$Date < '2012-11-11',4:ncol(t)]
smallzd = t[t$Date>='2012-10-21' & t$Date < '2012-11-11',]

out = read.csv("results/link_50_normalize_outlier_scores.csv")
out$date = as.character(out$date)
smallout = out[out$date>='2012-10-21' & out$date < '2012-11-11',]


print(dim(smallz))
old = read.csv("results/outlier_scores.csv")
old$date = as.character(old$date)
#smallold = old[19537 : (19537+168*40) , ]
smallold = old[old$date>='2012-10-21' & old$date < '2012-11-11',]

print(dim(smallold))


pdf("outlier_scores_tmp.pdf", 100/2, 20/2)

l1_norm=rowSums(abs(smallz) / rowSums(smallz != 0))
l1=rowSums(abs(smallz) / ncol(smallz))
l2=sqrt(rowSums(smallz^2 / ncol(smallz)))
l2_norm=sqrt(rowSums(smallz^2 / rowSums(smallz != 0)))

plot(l1_norm, type="l", lwd=1, ylim=range(l2_norm))
lines(l1, type="l", lwd=1, col="red")
lines(l2, type="l", lwd=1, col="green")
lines(l2_norm, type="l", lwd=4, col="blue")
lines(smallout$mahal, type="l", lwd=3, col="purple")


legend("topright", legend=c("L1 normalized", "Mahal normalized", "L1", "Mahal"), col=c("black", "blue", "red", "green"), lwd=2, bg="white")

abline(v=(1:400)*24)

plot(smallold$mahal, type="l")


dev.off()


pdf("zscore_hists.pdf", 20, 10)
print(paste("Making", nrow(smallz)))
for(i in 1:nrow(smallz)){
	title = paste(smallzd$Date[i], smallzd$Hour[i], ":", sum(smallz[i,] !=0))
	print(title)
	truncated = pmax(pmin(as.numeric(smallz[i,]), 5), -5)
	truncated = truncated[truncated!=0]
	hist(truncated, main=title, breaks=seq(-5,5,.2), xlim=c(-5,5))
}

dev.off()





pdf("outlier_scores_acf.pdf", 20, 10)
l1_norm_acf = acf(l1_norm, lag.max=336, plot=F)$acf
l2_norm_acf = acf(l2_norm, lag.max=336, plot=F)$acf
l1_acf = acf(l1, lag.max=336, plot=F)$acf
l2_acf = acf(l2, lag.max=336, plot=F)$acf

plot(l1_norm_acf, col="black", lwd=2, type="l", xlab="time shift (hours)", ylab="correlation")
lines(l1_acf, col="red", lwd=2)
lines(l2_acf, col="green", lwd=2)
lines(l2_norm_acf, col="blue", lwd=3)

legend("topright", legend=c("L1 normalized", "Mahal normalized", "L1", "Mahal"), col=c("black", "blue", "red", "green"), lwd=2, bg="white")

l2_acf=acf(smallold$mahal, lag.max=336, plot=F)$acf
plot(l2_acf, type="l", lwd=2, xlab="time shift (hours)", ylab="correlation")


dev.off()






