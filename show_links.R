library(RgoogleMaps)
clat = 40.773455
clon = -73.982880
z = 12

#jet.colors =colorRamp(c("#00007F", "blue", "#007FFF", "cyan",
#                     "#7FFF7F", "yellow", "#FF7F00", "red", "#7F0000"))

jet.colors =colorRamp(rev(c("blue", "#007FFF", "cyan",
                     "#7FFF7F", "yellow", "#FF7F00", "red")))


linearScale = function(x, lo, hi){
	x = (x - lo) / (hi - lo)
	return(pmax(pmin(x, 1), 0))
}








infile = paste("tmp.csv")



print(paste("Reading", infile))



full_t = read.csv(infile)

#t$speed[is.na(t$speed)] = 0

for(thresh in c(1,2,3,4,5,6,7,8,9,10,15,20,25,30,40,50,60,70,80,90,100,150,200,250,300)){

#outfile = paste("results/maps/map_thresh", thresh, ".png", sep="")

outfile = sprintf("results/maps2/map_thresh%05d.png", 10000 - thresh)
png(outfile, 1024, 1024)
#par(mar=c(2,5,3,2), family="sans", bg="black", col.axis="white",col.lab="white", fg="white")


t = full_t[full_t$avg_num_trips>=thresh,]
par(mar=c(2,5,3,2), family="sans", bg="black", col.axis="white",col.lab="white", fg="white")
plot(0,0,type="n", xlim=range(full_t$begin_lon, full_t$end_lon), ylim=range(full_t$begin_lat, full_t$end_lat))

segments(x0=t$begin_lon, y0=t$begin_lat, x1=t$end_lon, y1=t$end_lat, add=T, col="white",lwd=3)

par(mar=c(1,1,3,1))
my_title = sprintf("Links with at least %d trips/hour", thresh)
title(main=my_title, cex.main=3, col.main="white")





dev.off()
}

