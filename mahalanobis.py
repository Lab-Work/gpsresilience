# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 19:28:30 2014

@author: Brian Donovan (briandonovan100@gmail.com)
"""
from tools import *
from numpy import transpose, matrix
from numpy.linalg import inv, eig
from math import sqrt



#Represents a set of statistics for a group of mean pace vectors
#Technically, it stores the moments, sum(1), sum(x), sum(x**2)
class GroupedStats:
	def __init__(self, group_of_vectors):
		self.count = 0
		self.s_x = 0
		self.s_xxt = 0
		
		#Iterate through mean pace vectors, updating the counts and sums
		for meanPaceVector in group_of_vectors:
			if(allNonzero(meanPaceVector)):
				self.s_x += meanPaceVector
				self.s_xxt += meanPaceVector * transpose(meanPaceVector)
				self.count += 1
	
	#Make a copy of this GroupedStats object
	#returns: A GroupedStats object, identical to this one
	def copy(self):
		#generate an empty GroupedStats
		cpy = GroupedStats([])
		
		#copy values from this GroupedStats
		cpy.count = self.count
		cpy.s_x = matrix(self.s_x)
		cpy.s_xxt = matrix(self.s_xxt)
		
		#return the copy
		return cpy
	
	#Use the GroupedStats to compute the
	#returns:
		#(mean, cov)  Breakdown:
		#mean - A numpy column vector, representing the mean of all observations
		#cov - A numpy matrix, representing the covariance of all observations
	def getMeanAndCov(self):
		#E(x) = sum(x) / n
		mean = self.s_x / self.count
		
		#var(x) = E[x**2] - E[x]**2.  Multiply by n/(n-1) for unbiased covariance correction
		cov = (self.s_xxt / self.count - (mean * transpose(mean))) * (self.count / (self.count - 1))
		
		return (mean, cov)
	
	#Generates a leave-1-out estimate of the group stats.
	#In other words, the variables (count, s_x, s_xxt) will calculated as if a given vector is discluded
	#This is faster than re-generating the stats with a set of vectors that does not include "vect"
	#params:
		#vect - the vector to be "left out"
	#returns:
		#a new GroupedStats that does not contain the information from vect
	def generateLeave1Stats(self, vect):
		#copy self
		newStats = self.copy()
		
		#subtract the leave-one-out vector from the sums
		if(allNonzero(vect)):
			#note - vectors with missing data were not used to create the sums
			#so they should not be subtracted
			newStats.count -= 1
			newStats.s_x -= vect
			newStats.s_xxt -= vect * transpose(vect)
		return newStats
	
	#Returns the mahalanobis distance of a vector from the mean
	#This is one way of measuring how much of an outlier that vector is
	#params:
		#vector - A vector to measure
	#returns a positive number representing the mahalanobis distance
	def mahalanobisDistance(self, vect):
		(mean, cov) = self.getMeanAndCov()
		try:
			mahal = transpose(vect - mean) * inv(cov) * (vect - mean)
			return sqrt(mahal[0,0])
		except:
			print vect
			(vects, vals) = eig(cov)
			print vects
			print vals
		
		
#Computes the mahalanobis distance of each vector from the mean
#Using a leave-one-out estimate
#params:
	#vectors - a list of Numpy vectors
#returns:
	# a list of Mahalanobis distances,  correspondign to the input vectors
def computeMahalanobisDistances(vectors):
	#compute the groupedStats for the vectors	
	groupedStats = GroupedStats(vectors)
	
	distances = []
	#We want to compute the Mahalanobis distance for each vector
	for vect in vectors:
		#Get the leave-one-out stats
		stats = groupedStats.generateLeave1Stats(vect)
		#stats = groupedStats
		#Use these to compute the mahalanobis distance from this vector, and add to list
		mahalanobisDistance = stats.mahalanobisDistance(vect)
		distances.append(mahalanobisDistance)
	
	#finally, return the computed distances
	return distances