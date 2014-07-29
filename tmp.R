pdf("tmp.pdf", 200, 5)

#lnl plot
t = read.csv("results/lnl_over_time_1tail.csv")
t$date = as.character(t$date)
s = t

plot(s$lnl_norm, col="black", type="l", main="Log-Likelihood Event Detection", xaxt="n", xlab="", ylab="Log-Likelihood")
ids = (0:21) * 24 + 1
axis(1, at=ids, labels=s$date[ids], las=3, cex.axis=.7)
lines(s$lnl_smooth, col="blue", lwd=2)

thresh = quantile(t$lnl_norm, .05)
abline(h=thresh, col="red", lwd=2, lty=1)