import csv
from grid import *
import math
import Image

EARTH_RADIUS = 3963.1676
BOUNDARY_FILE_NAME = "4regions_boundary.png"


#0 = E = white (255,255,255,255)
#1 = U = green (0  ,255,0  ,255)
#2 = M = blue  (0  ,0  ,255,255)
#3 = L = red   (255,0  ,0  ,255)

class ColorMap:
	def __init__(self, map_filename, coords):
		(self.left, self.top, self.right, self.bottom) = coords
		im = Image.open(map_filename)
		pix = im.load()
		
		self.p_width = im.size[0]
		self.p_height = im.size[1]
		
		#allocate space
		self.p_array = [[0] *im.size[1] for x in range(im.size[0])]
		for x in range(im.size[0]):
			for y in range(im.size[1]):
				col = pix[x,y]
				if(col==(255,255,255,255)):
					self.p_array[x][y] = 0
				elif(col==(0,255,0,255)):
					self.p_array[x][y] = 1
				elif(col==(0,0,255,255)):
					self.p_array[x][y] = 2 
				elif(col==(255,0,0,255)):
					self.p_array[x][y] = 3
				else:
					self.p_array[x][y] = 4
	
	
	"""
	$ll
	          lat       lon
	[1,] 40.68289 -74.08339
	
	$ur
	         lat       lon
	[1,] 40.8493 -73.86366
	"""	
	def nearestPixel(self, lat, lon):
		x = int(((lon - self.left) / (self.right - self.left)) * self.p_width)
		y = self.p_height - int(((lat - self.bottom) / (self.top - self.bottom)) * self.p_height)
		
		x = max(x,0)
		x = min(x,self.p_width-1)
		y = max(y,0)
		y = min(y,self.p_height-1)

		
		return (x,y)
	
	def colorAt(self, lat, lon):
		(x,y) = self.nearestPixel(lat, lon)
		return self.p_array[x][y]
		
		
		



class Region:
	id = 0
	name = ""
	def __init__(self, id, name):
		self.id = id
		self.name = name
	def __str__(self):
		return str(self.name)
		

class RegionSystem(GridSystem):
	def __init__(self, dirName):
		self.cells = []
		east = Region(0, "E")
		up = Region(1,"U")
		mid = Region(2, "M")
		low = Region(3, "L")
		self.cells = [east, up, mid, low]
		self.colorMap = ColorMap(BOUNDARY_FILE_NAME, (-74.08339, 40.8493, -73.86366, 40.68289))		
		
		self.dirName = dirName
		self.begin()
		
	

	def getCell(self, lon, lat):
		"""
		#rightline = c(40.802782,-73.920135, 40.705515,-73.98571)
		if(lat < (lon - -73.920135)*1.4832939382387935 + 40.802782):
			return self.cells[0]
		
		#topline = c(40.773596,-73.995152, 40.757474,-73.955669)
		if(lat > (lon - -73.995152)*(-0.4083276346780654) + 40.773596):
			return self.cells[1]
			
		#bottomline = c(40.743039,-74.010258,40.723787,-73.964939)
		if( lat > (lon - -74.010258)*(-0.42481078576325493) + 40.743039):
			return self.cells[2]
		
		return self.cells[3]
		"""
		region = self.colorMap.colorAt(lat, lon)
		if(region==4):
			return None
		return self.cells[region]
	
if(__name__=="__main__"):
	r = csv.reader(open("sample_data.csv", "r"))
	w = csv.writer(open("region_tmp.csv", "w"))
	w.writerow(["col", "lat", "lon"])
	system = RegionSystem("blah")
	header = True
	
	
	for line in r:
		if(header):
			myheader = {}
			for i in range(len(line)):
				myheader[line[i].strip()] = i
			header = False
		else:
			lat = float(line[myheader["pickup_latitude"]])
			lon = float(line[myheader["pickup_longitude"]])
			
			c = system.getCell(lon, lat)
			if(c==system.cells[0]):
				w.writerow(["white", lat, lon])
			if(c==system.cells[1]):
				w.writerow(["green", lat, lon])
			if(c==system.cells[2]):
				w.writerow(["blue", lat, lon])
			if(c==system.cells[3]):
				w.writerow(["red", lat, lon])
			if(c==None):
				w.writerow(["black",lat, lon])
				
			
			
		
