# -*- coding: utf-8 -*-
"""
Created on Wed Sep 24 12:34:53 2014

@author: brian
"""
from tools import *
from Queue import PriorityQueue



def getPairwiseDist(vects):
	dist =[[0]*len(vects) for x in range(len(vects))]
	for i in range(len(vects)):
		for j in range(len(vects)):
			dist[i][j] = euclideanDist(vects[i], vects[j])
			dist[j][i] = dist[i][j]
	return dist

def getLocalOutlierFactors(vects, k):
	
	#TMP HACK
	return [0]*len(vects)
	pairDist = getPairwiseDist(vects)
	

	#The list of neighbor ids for each point
	neighbors = [None for x in range(len(vects))]
	#Populate each of these lists with the k nearest neighbors
	for i in range(len(vects)):
		pq = PriorityQueue()
		for j in range(len(vects)):
			if(i != j):
				pq.put((-pairDist[i][j], j))
				if(pq.qsize() > k):
					pq.get()
		neighbors[i] = [neighborId for (negDist, neighborId) in pq.queue]
		
	#print("neighbors " + str(neighbors))
	
	#For each point, the distance to its kth nearest neighbor
	kDist = [0] * len(vects)
	for i in range(len(vects)):
		for j in neighbors[i]:
			kDist[i] = max(kDist[i], pairDist[i][j])
	
	#print("kdist " + str(kDist))
			
			
	
	#local reachability density - the inverse of the average reachability distance to all of my neighbors
	lrd = [0] * len(vects)
	
	for i in range(len(vects)):
		#first compute the sum
		for j in neighbors[i]:
			lrd[i] += max(kDist[j], pairDist[i][j])
		#normalize and invert in one step
		lrd[i] = k / lrd[i]
	
	#print("lrd " + str(lrd))
	
	#local outlier factor - average ratio  of neighbor densities to my density
	lof = [0] * len(vects)
	for i in range(len(vects)):
		#first compute the sum
		for j in neighbors[i]:
			lof[i] += lrd[j]
		#normalize and divide by my density
		lof[i] = lof[i] / (k*lrd[i])
	
	#print("lof " + str(lof))
	
	return lof
	
	
	
	