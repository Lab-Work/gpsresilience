t = read.csv('results/regions_missing_data.csv')

pdf('results/regions_missing_data.pdf')
region_nums = unique(t$num_regions)


jet.colors =colorRamp(c("#00007F", "blue", "#007FFF", "cyan",
                     "#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))


plot(t$dimension, t$perc_missing, type="n", xlab="OD Pair", ylab="Missing Data", xlim=c(0,600))
for(i in 1:length(region_nums)){
	k = region_nums[i]
	s = t[t$num_regions==k,]
	mycol = rgb(jet.colors(i/length(region_nums))/255)
	lines(s$dimension, s$perc_missing, col=mycol)
}
rgb(jet.colors(1:length(region_nums)/region_nums)/255)
legend("bottomright", legend=paste(region_nums, "Regions"), col=rgb(jet.colors(1:length(region_nums)/length(region_nums))/255), lwd=2, bg="white")


plot(t$dimension_frac, t$perc_missing, type="n", xlab="OD Pair Quantile", ylab="Missing Data")
for(i in 1:length(region_nums)){
	k = region_nums[i]
	s = t[t$num_regions==k,]
	mycol = rgb(jet.colors(i/length(region_nums))/255)
	lines(s$dimension_frac, s$perc_missing, col=mycol)
}
legend("bottomright", legend=paste(region_nums, "Regions"), col=rgb(jet.colors(1:length(region_nums)/length(region_nums))/255), lwd=2, bg="white")



tol_vals=c(.01,.05,.10,.2)
plot(0,0,type="n", xlim=range(region_nums), ylim=range(0,100), xlab="Number of Regions", ylab="Valid OD Pairs")
for(i in 1:length(tol_vals)){
	tol = tol_vals[i]
	p_missing_vect = numeric(length(region_nums))
	for(j in 1:length(region_nums)){
		k = region_nums[j]
		p_missing_vect[j] = sum(t$num_regions==k & t$perc_missing <= tol)
	}
	lines(region_nums, p_missing_vect, col=i)
}

legend("topleft", legend=paste(tol_vals, "Missing Data Allowed"), col=1:length(tol_vals), lwd=2)





tol_vals=c(.01,.05,.10,.2)
plot(0,0,type="n", xlim=range(region_nums), ylim=range(0,1), xlab="Number of Regions", ylab="Fraction of Valid OD Pairs")
for(i in 1:length(tol_vals)){
	tol = tol_vals[i]
	p_missing_vect = numeric(length(region_nums))
	for(j in 1:length(region_nums)){
		k = region_nums[j]
		p_missing_vect[j] = sum(t$num_regions==k & t$perc_missing <= tol) / sum(t$num_regions==k)
	}
	lines(region_nums, p_missing_vect, col=i)
}

legend("topright", legend=paste(tol_vals, "Missing Data Allowed"), col=1:length(tol_vals), lwd=2)

