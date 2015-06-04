"""
An extension to grid.py which allows for arbitrarily-shaped regions.  Region boundaries are loaded from a color-coded image file.
Currently supports a map of NYC which has 4 regions

Created on Sat May  3 12:33:42 2014

@author: Brian Donovan (briandonovan100@gmail.com)
"""
import csv
from grid import *
import Image

BOUNDARY_FILE_NAME = "4regions_boundary.png"


#0 = E = white (255,255,255,255)
#1 = U = green (0  ,255,0  ,255)
#2 = M = blue  (0  ,0  ,255,255)
#3 = L = red   (255,0  ,0  ,255)
#4 = ? = black (0  ,0  ,0  ,255)

#Represents a colored map image.  I.E. a picture with some latitude/longitude bounds
#It is possible to query the color of a pixel at arbitrary coordinates in CONSTANT TIME
class ColorMap:
    #Initialize the ColorMap with the region picture and the coordinate bounds that the picture corresponds to in reality
    #Arguments:
        #map_filename - a file which contains a color-coded map
        #coords - the lat/lon bounds of this image in clockwise order: (left_lon, top_lat, right_lon, bottom_lat)
    def __init__(self, map_filename, coords):
        #Unpack the coordinates
        (self.left, self.top, self.right, self.bottom) = coords
        
        #Open the image for pixel-level access
        im = Image.open(map_filename)
        pix = im.load()
        
        #Get the pixel size of the image
        self.p_width = im.size[0]
        self.p_height = im.size[1]
        
        #allocate space.  NxM array based on image size
        self.p_array = [[0] *im.size[1] for x in range(im.size[0])]
        
        #Assign integers into the array based on pixel colors
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
    

    #Convert latitutde and longitude into pixel coordinates.
    #If they fall outside the bounds of the picture, the nearst pixel is given
    #Arguments:
        #lat - the query latitude
        #lon - the query longitude
    #Returns:
        # a tuple (x, y) corresponding to pixel coordinates
    def nearestPixel(self, lat, lon):
        
        #Scales the lat/lon coordinates to pixel coordinates, using the map bounds and image size
        #This is a simple linear transformation, which assumes that the earth is flat
        x = int(((lon - self.left) / (self.right - self.left)) * self.p_width)
        #Note that pixel y-coordinates are reversed, since the image starts at the top
        y = self.p_height - int(((lat - self.bottom) / (self.top - self.bottom)) * self.p_height)
        
        #Force the coordinates to be within the bounds of the image
        x = max(x,0)
        x = min(x,self.p_width-1)
        y = max(y,0)
        y = min(y,self.p_height-1)

        
        return (x,y)
    
    #Determines the color of the map at a given latitude/longitude
    #Arguments:
        #lat - the query latitude
        #lon - the query longitude
    def regionAt(self, lat, lon):
        (x,y) = self.nearestPixel(lat, lon)
        if(self.p_array[x][y]==4):
            return None

        return self.p_array[x][y]

# Simple wrapper class, which stores a Map object, and can quickly find the
# region id for a given coordinate, by examining the region_id of the nearest
# node to that coordinate.  Has the same interface as ColorMap
class GraphMap:
    def __init__(self, road_map, use_cache=False, cache_size=10000):
        self.road_map = road_map
        
        if(use_cache):
            self.cache_size = cache_size
            self.cache = [[None]*cache_size for x in xrange(cache_size)]
        else:
            self.cache = None

    def regionAt(self, lat, lon):
        
        if(self.cache==None):
            nearest_node = self.road_map.get_nearest_node(lat, lon)
            
            if(nearest_node==None):
                return None
                
            return nearest_node.region_id
        else:
            i = int( self.cache_size * (lon - self.road_map.min_lon) / (self.road_map.max_lon - self.road_map.min_lon))
            j = int( self.cache_size * (lat - self.road_map.min_lat) / (self.road_map.max_lat - self.road_map.min_lat))
            if(i < 0 or i >= self.cache_size or j < 0 or j >= self.cache_size):
                return None
            
            if(self.cache[i][j]==None):
                mid_lon = (i+.5)/self.cache_size * (self.road_map.max_lon - self.road_map.min_lon)
                mid_lat = (j+.5)/self.cache_size * (self.road_map.max_lat - self.road_map.min_lat)
                self.cache[i][j] = self.road_map.get_nearest_node(mid_lat, mid_lon)
            
            return self.cache[i][j]
                
    
    def getCells(self):
        unique_regions = set()
        for node in self.road_map.nodes:
            unique_regions.add(node.region_id)
        
        cells = [Region(r_id, "r%d"%r_id) for r_id in sorted(unique_regions)]
        return cells
            


#A region of arbitrary shape.  A replacement for the Cell object, seen in grid.py
#contains minimal information
class Region:
    id = 0
    name = ""
    def __init__(self, id, name):
        self.id = id
        self.name = name
        
    def __str__(self):
        return str(self.name)
    
        

#Extends GridSystem by allowing for arbitrarily shaped regions
#This is done by overriding the getCell() method
class RegionSystem(GridSystem):
    #Simple constructor, designed for NYC regions
    #Arguments:
        #dirName - the folder in which to output files
    def __init__(self, dirName, road_map):
        
        """         
        #OLD CODE that manually specifies regions via an image file
        east = Region(0, "E")
        up = Region(1,"U")
        mid = Region(2, "M")
        low = Region(3, "L")
        self.cells = [east, up, mid, low]
        
        #Load the colored map from file with the appropriate boundaries
        self.regionMap = ColorMap(BOUNDARY_FILE_NAME, (-74.08339, 40.8493, -73.86366, 40.68289))        
        """      
        
        self.regionMap = GraphMap(road_map, use_cache=True)
        self.cells = self.regionMap.getCells()
        
        
        #Save the dirName
        self.dirName = dirName
        
        #Open files for output
        self.begin()
        
    
    #Determines which cell a given coordinate falls in
    #Arguments:
        #lon - the query longitude
        #lat - the query latitude
    #Returns:
        #The region that the coordinates fall in
    def getCell(self, lon, lat):
        #Determine the color of the map at that coordinate
        region = self.regionMap.regionAt(lat, lon)
        
        #4 Corresponds to an untracked region - return None
        if(region==None):
            return None
        
        #The cells are indexed by the color index
        return self.cells[region]
    
#A simple unit test
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
                
            
            
        
