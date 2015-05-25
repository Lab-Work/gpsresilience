error.bars<-function(x,y,stderr,length=.1,...) {
  ylim<-c(min(y-stderr),max(y+stderr))
  upy<-y+stderr
  downy<-y-stderr
  arrows(x,y,x,upy,angle=90,length=length, ...)
  arrows(x,y,x,downy,angle=90,length=length, ...)
 }



t = read.csv('eigen_counts.csv')

gamma_vals = sort(unique(t$gamma))
avg = numeric(length(gamma_vals))
esd = numeric(length(gamma_vals))

for(i in 1:length(gamma_vals)){
	gamma = gamma_vals[i]
	print(gamma)
	avg[i] = mean(t$num_eigen[t$gamma==gamma])
	esd[i] = sd(t$num_eigen[t$gamma==gamma])
}


pdf("results/eigen_counts.pdf")
plot(gamma_vals, avg, type="l", xlab="Gamma", ylab="# Nonzero Eigenvalues", main="Number of Nonzero Eigenvalues")
error.bars(gamma_vals, avg, esd)




for(i in 1:length(gamma_vals)){
	gamma = gamma_vals[i]
	evs = t$num_eigen[t$gamma==gamma]
	tab = as.data.frame(table(evs))
	print(tab)
	my_title = paste("Distribution of Number of EVs when gamma=", gamma)
	barplot(tab$Freq, names.arg=tab$evs, xlab ="Num Eigenvalues", ylab="Frequency", main=my_title)
}



dev.off()
