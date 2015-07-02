t = read.csv('results/coarse_montecarlo.csv')

pdf('results/sandy_coarse_duration_hist.pdf', 10, 3)
hist(t$duration[t$event=='Sandy 2012-10-28 21:00:00'], breaks=100, xlab="Event Duration", main="Hurricane Sandy Duration\nOrigin-Destination Method")
dev.off()


t = read.csv('results/fine_montecarlo.csv')

pdf('results/sandy_fine_duration_hist.pdf', 10, 3)
hist(t$duration[t$event=='Sandy 2012-10-28 21:00:00'], breaks=100, xlab="Event Duration", main="Hurricane Sandy Duration\nLink-Level Method)
dev.off()
