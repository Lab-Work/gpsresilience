# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 20:10:23 2014

@author: brian
"""

from mvGaussian import *
from numpy import matrix, array_equal, diag, concatenate, cov

#A class that represents a probability distribution, given by a kernel density estimate
#The kernel is Gaussian, and the bandwidth matrix is chosen by the "normal optimal smoothing" method
#Given by Bowman and Azzalini.  See "Applied Smoothing Techniques for Data Analysis"
class MVGaussianKernel:
	#Constructor which initializes the distribution from a set of observations
	#Arguments:
		#obs - a list of Numpy column vectors
	def __init__(self, obs):
		
		#diag_list = [spherical_bandwidth**2] * len(obs)
		#sig = matrix(diag(diag_list))
		
		#Compute the optimal bandwidth
		sig = self.computeBandwidthMatrix(obs)

		#Temporary distribution which will be copied
		#This is faster than calling the MVGaussian.__init__() over and over
		#because there is no need to invert the covariance matrix repeatedly
		reference_distribution = MVGaussian(obs[0], sig)
		
		#Each observation gets one small gaussian distribution - the KDE is the average of all of these densities
		self.distributions = []
		for vect in obs:
			if(allNonzero(vect)):
				#As mentioned before, the distributions are copied instead of generated indepedently
				#They all have the same covariance matrix, but different means
				distribution = reference_distribution.copy()
				distribution.mu = vect	#alter the mean
				self.distributions.append(distribution)
	
	#Chooses a bandwidth (i.e. length-scale, smoothing parameter, etc...) which is appropriate for the given data	
	#The bandwidth matrix is chosen by the "normal optimal smoothing" method
	#Given by Bowman and Azzalini.  See "Applied Smoothing Techniques for Data Analysis"
	#Arguments:
		#obs - a list of Numpy column vectors
	#Returns:
		#a Numpy matrix
	def computeBandwidthMatrix(self, obs):
		#Compute the variance of each dimension (diagonal entries of the covariance matrix)
		data_matrix = concatenate(obs, axis=1)
		cov_matrix =  matrix(cov(data_matrix))
		diag_cov = diag(diag(cov_matrix))
		
		n = len(obs)		#Number of observations
		p = len(obs[0])	#Dimension of observations
		
		#Given by the formula in the book.
		#Note that the exponent becomes 2/(p+4) instead of(1/p+4) because we are computing variance.
		#The book gives an equation for standard deviation - we have to square it
		scaling_factor = (4.0/((p+2)*n)) ** ((2.0)/(p+4)) 
		
		#Scale the diagonal covariance matrix
		return diag_cov * scaling_factor	
		
	
	def loglik_scaled(self, obs):
		#Initialize the probabilities with really low numbers
		log_ps = [-100000] * len(self.distributions)
		count = 0
		for i in range(len(self.distributions)):
			#Leave one out estimate - ignore the observation itself when computing the density from its neighbors
			if(not array_equal(obs, self.distributions[i].mu)):
				#Compute the log-probability-density due to one of the distributions
				log_ps[i] = self.distributions[i].gaussian_loglik(obs)
				count += 1
		
		#Compute the mean of all of these probabilities (note that they are in log-space)
		return addLogs(log_ps) - count


if (__name__=="__main__"):
	pass		