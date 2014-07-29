#library(png)



#plot(t$pickup_longitude, t$pickup_latitude, pch=20, cex=.5, col="green")
#points(t$dropoff_longitude, t$dropoff_latitude, pch=20, cex=.5, col="red")

#img = readPNG("region.png")
#rasterImage(img, -74.81632, -72.86384, 39.71112, 41.36187)



#39.71112 41.36187
#-74.81632 -72.86384


library(RgoogleMaps)
 
#load("add destination to data here")
#mymarkers <- cbind.data.frame(lat = bergen$Lat, lon = bergen$Lon)
#bb <- qbbox(lat= mymarkers[, "lat"], lon = mymarkers [, "lon"])
# zoom <-min(MaxZoom(latrange=bb$latR, lonrange=bb$lonR))

clat = 40.78737
clon = -73.9888


MyMap <- GetMap(center=c(clat,clon), zoom = 10, destfile = "tmp.map", maptype = "mobile", GRAYSCALE=FALSE)
 


#clat = 40.75737
#clon = -73.9

clat = 40.766276
clon = -73.973694

#rightline = c(40.802782,-73.920135, 40.705515,-73.98571)
#topline = c(40.773596,-73.995152, 40.757474,-73.955669)
#bottomline = c(40.743039,-74.010258,40.723787,-73.964939)

#right-top : (40.755876764069, -73.95175734721103)
#right-bottom : (40.72657828523506, -73.97150965528607)


rightline = c(40.802782,-73.920135, 40.705515,-73.98571)
topline = c(40.773596,-73.995152, 40.755876764069, -73.95175734721103)
bottomline = c(40.743039,-74.010258,40.72657828523506, -73.97150965528607)


l = rbind(rightline, topline, bottomline)

MyMap <- GetMap(center=c(clat,clon), zoom = 12, destfile = "tmp.map", maptype = "mobile", GRAYSCALE=FALSE)




t = read.csv("region_tmp.csv")
png("4regions2.png", 1280, 1280)
cz = as.character(t$col)
print(cz)
tmp = PlotOnStaticMap(MyMap,lat = t$lat, lon = t$lon, cex=1,pch=20, col=cz)


dev.off()

