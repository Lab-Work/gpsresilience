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


trips = read.csv("trip_links.csv")
#t$speed[is.na(t$speed)] = 0


outfile = "results/routes/route.png"
png(outfile, 1024, 1024)
#par(mar=c(2,5,3,2), family="sans", bg="black", col.axis="white",col.lab="white", fg="white")


t = full_t[full_t$avg_num_trips>=0,]
par(mar=c(2,5,3,2), family="sans", bg="black", col.axis="white",col.lab="white", fg="white")
plot(0,0,type="n", xlim=range(full_t$begin_lon, full_t$end_lon), ylim=range(full_t$begin_lat, full_t$end_lat))

segments(x0=t$begin_lon, y0=t$begin_lat, x1=t$end_lon, y1=t$end_lat, col="white",lwd=3)


route_lwd=6

s = trips[trips$trip_id==10,]
segments(x0=s$from_lon, y0=s$from_lat, x1=s$to_lon, y1=s$to_lat, col="blue",lwd=route_lwd)


s = trips[trips$trip_id==57,]
segments(x0=s$from_lon, y0=s$from_lat, x1=s$to_lon, y1=s$to_lat, col="green",lwd=route_lwd)


s = trips[trips$trip_id==43,]
segments(x0=s$from_lon, y0=s$from_lat, x1=s$to_lon, y1=s$to_lat, col="red",lwd=route_lwd)

s = trips[trips$trip_id==64,]
segments(x0=s$from_lon, y0=s$from_lat, x1=s$to_lon, y1=s$to_lat, col="blue",lwd=route_lwd)

s = trips[trips$trip_id==88,]
segments(x0=s$from_lon, y0=s$from_lat, x1=s$to_lon, y1=s$to_lat, col="green",lwd=route_lwd)

s = trips[trips$trip_id==71,]
segments(x0=s$from_lon, y0=s$from_lat, x1=s$to_lon, y1=s$to_lat, col="red",lwd=route_lwd)
dev.off()

