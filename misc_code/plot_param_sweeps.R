t = read.csv('param_sweep.csv')
t$iter = rep(1,nrow(t))

n_tols = length(unique(t$tol))

jet.colors =colorRamp(c("#00007F", "blue", "#007FFF", "cyan",
                     "#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))







pdf('param_sweep.pdf')


plot(0,0,type="n", xlim=range(t$gamma), ylim=range(t$rank), xlab="gamma", ylab="PCA Rank", main="Tuning Gamma and Tol")

i = 0
for(tol in sort(unique(t$tol))){
	i = i + 1
	s = t[t$tol==tol,]
	mycol = rgb(jet.colors(i/n_tols)/255)
	lines(s$gamma, s$rank, col=mycol)
}
legend('bottomright', legend=paste("tol=", sort(unique(t$tol))), col=rgb(jet.colors((1:n_tols)/n_tols)/255), lwd=2, bg="white", cex=.5)



plot(0,0,type="n", xlim=range(t$gamma), ylim=range(t$outliers), main="Tuning Gamma and Tol", xlab="gamma", ylab="Percent Outliers")

i = 0
for(tol in sort(unique(t$tol))){
	i = i + 1
	s = t[t$tol==tol,]
	mycol = rgb(jet.colors(i/n_tols)/255)
	lines(s$gamma, s$outliers, col=mycol)
}
legend('topright', legend=paste("tol=", sort(unique(t$tol))), col=rgb(jet.colors((1:n_tols)/n_tols)/255), lwd=2, bg="white", cex=.5)





plot(0,0,type="n", xlim=range(t$gamma), ylim=range(t$iter), main="Tuning Gamma and Tol", xlab="gamma", ylab="Num Iterations")

i = 0
for(tol in sort(unique(t$tol))){
	i = i + 1
	s = t[t$tol==tol,]
	mycol = rgb(jet.colors(i/n_tols)/255)
	lines(s$gamma, s$iter, col=mycol)
}
legend('bottomright', legend=paste("tol=", sort(unique(t$tol))), col=rgb(jet.colors((1:n_tols)/n_tols)/255), lwd=2, bg="white", cex=.5)
