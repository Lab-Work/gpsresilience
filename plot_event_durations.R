t = read.csv('results/event_duration_comparison.csv')

events = unique(t$event)

pdf('results/event_region_sensitivity.pdf')
plot(t$num_regions, t$duration, type="n", main="Sensitivity to Number of Regions", xlab="Number of Regions", ylab="Event Duration")
for(i in 1:length(events)){
	event = events[i]
	s = t[t$event==event,]
	lines(s$num_regions, s$duration, col=i, lwd=2)
}

legend("topleft", legend=events, col=1:length(events), lwd=2, cex=.5, bg="white")

dev.off()



