t = read.csv('param_sweep.csv')


pdf('param_sweep.pdf')


plot(0,0,type="n", xlim=range(t$gamma), ylim=range(t$rank), xlab="gamma", ylab="PCA Rank", main="Tuning Gamma and Tol")

i = 1
for(tol in sort(unique(t$tol))){
	i = i + 1
	s = t[t$tol==tol,]
	lines(s$gamma, s$rank, col=i)
}
legend('bottomright', legend=paste("tol=", sort(unique(t$tol))), col=2:9, lwd=2, bg="white")



plot(0,0,type="n", xlim=range(t$gamma), ylim=range(t$outliers), main="Tuning Gamma and Tol", xlab="gamma", ylab="Percent Outliers")

i = 1
for(tol in sort(unique(t$tol))){
	i = i + 1
	s = t[t$tol==tol,]
	lines(s$gamma, s$outliers, col=i)
}
legend('topright', legend=paste("tol=", sort(unique(t$tol))), col=2:9, lwd=2, bg="white")





plot(0,0,type="n", xlim=range(t$gamma), ylim=range(t$iter), main="Tuning Gamma and Tol", xlab="gamma", ylab="Num Iterations")

i = 1
for(tol in sort(unique(t$tol))){
	i = i + 1
	s = t[t$tol==tol,]
	lines(s$gamma, s$iter, col=i)
}
legend('bottomright', legend=paste("tol=", sort(unique(t$tol))), col=2:9, lwd=2, bg="white")
