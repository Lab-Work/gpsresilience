# -*- coding: utf-8 -*-
"""
A class which represents the multivariate Gaussian distribution.
Implements likelihood functions and log-likelihood functions.

Created on Wed May 21 17:38:31 2014

@author: Brian Donovan (briandonovan100@gmail.com)
"""


from numpy import  transpose, zeros, trace
from numpy.linalg import inv, det, eig
from math import log, pi, sqrt, exp

from tools import *

class InvalidVectorException(Exception):
	pass

class InvalidCovarianceException(Exception):
	def __init__(self, sigma, reason):
		self.sigma = sigma
		self.reason = reason
	def __str__(self):
		#vals, vects = eig(self.sigma)
		#return str(self.sigma) + "\n" + self.reason + "\n Eigenvals : " + str(self.vals)
		return str(self.sigma) + "\n" + self.reason
		

#Represents a multivariate Gaussian distribution.  Likelihood can be evaluated in several ways
class MVGaussian():
	#Initializes the distribution from the given parameters
	#Arguments:
		#mu - the mean vector.  Must be an Nx1 Numpy matrix (column vector)
		#sigma - the covariance matrix.  Must be an NxN Numpy matrix
	def __init__(self, mu=None, sig=None):
		
		if(mu==None and sig==None):
			return
		self.mu = mu
		self.sig = sig
		try:
			self.inv_sig = inv(sig)
		except:
			self.inv_sig = None
			#print("Non-invertible matrix")
			raise InvalidCovarianceException(sig, "Non-invertible matrix")
		self.determ = det(sig)
		if(self.determ < 0):
			#print ("Negative determinant")
			raise InvalidCovarianceException(sig, "Negative determinant")
		
		vals, vects = eig(self.sig)
		for v in vals:
			if(v < 0):
				#print ("Not positive definite")
				raise InvalidCovarianceException(sig, "Negative eigenvalue")
				
	#Generates a copy of this distribution.  Faster than calling the custructor again
	#because it doesn't need to invert the covariance matrix, compute the determinate,
	#or check the validity of the covariance matrix via eigen-decomposition
	def copy(self):
		other = MVGaussian()
		other.mu = self.mu
		other.sig = self.sig
		other.inv_sig = self.inv_sig
		other.determ = self.determ
		return other

	
	#If an observation has missing values, we need to take a subset of the dimensions
	#AKA the mean vector now has less than K dimensions where K <= N, and the cov matrix is K x K
	#This method performs the dimension selection
	#Arguments:
		#mu - the original N-dimensional mean vector
		#sig - the original NxN covariance matrix
		#obs - the observation which may have some missing values (0 is assumed to be missing)
		#returns a tuple containing the selection on these three inputs, as well as the inverse and determinant of the new matrix
	#Returns:
		#A tuple (mu_subset, sig_subset, inv_sig_subset, determ_subset, obs_subset).  Breakdown:
			#mu_subset - a Kx1 vector
			#sig_subset -a KxK matrix
			#inv_sig_subset - a KxK matrix, the inverse of sig_subset
			#determ_subset - a number. The determinant of sig_subset
			#obs_subset - a Kx1 vector
	def dimension_subset(self, mu, sig, obs, sig2=None):
		valid_ids = []
		#Loop through the dimensions of the observation - record the indexes with nonzero values
		for i in range(len(obs)):
			if(not obs[i]==0):
				valid_ids.append(i)
		
		#Time saver - return the original values if all of the dimensions are valid
		if(len(valid_ids)==len(sig)):
			if(sig2==None):
				return (mu, sig, self.inv_sig, self.determ, obs)
			else:
				return (mu, sig, self.inv_sig, self.determ, obs, sig2)
		elif(len(valid_ids)==0):
			#If no dimensions are valid, we cannot compute anything - throw an exception
			raise InvalidVectorException()
		
		#Perform the selection using Numpy slicing
		mu_subset = mu[valid_ids]
		sig_subset = sig[valid_ids,:][:,valid_ids]
		obs_subset = obs[valid_ids]
		
		#Compute the inverse and determinant of the matrix
		inv_sig_subset = inv(sig_subset)
		determ_subset = det(sig_subset)
		
		if(not sig2==None):
			sig2_subset = sig2[valid_ids,:][:,valid_ids]
			
			return (mu_subset, sig_subset, inv_sig_subset, determ_subset, obs_subset, sig2_subset)
			
		
		
		return (mu_subset, sig_subset, inv_sig_subset, determ_subset, obs_subset)		
	
	
	
	#The likelihood of obs, given this MVGaussian distribution
	#Params:
		#obs - the observed vector.  Must be an Nx1 Numpy matrix (column vector)
		#returns - a probability density
	def gaussian_likelihood(self, obs):
		
		try:
			(mu, sig, inv_sig, determ, obs) = self.dimension_subset(self.mu, self.sig, obs)
		except InvalidVectorException:
			return 0
		
		denom = sqrt((2*pi)**len(mu) * determ)
		pwr = -.5 * transpose(obs - mu) * inv_sig * (obs - mu)
		return (exp(pwr) / denom)[0,0]
	
	#The log-likelihood of obs, given this MVGaussian distribution
	#(Equivalent to taking the log of gaussian_likelihood, but more efficient)
	#Params:
		#obs - the observed vector.  Must be an Nx1 Numpy matrix (column vector)
		#returns - a log-probability density
	def gaussian_loglik(self, obs):
		
		if(self.inv_sig==None):
			return float('-inf')
		
		try:
			(mu, sig, inv_sig, determ, obs) = self.dimension_subset(self.mu, self.sig, obs)
		except InvalidVectorException:
			return 0		
		
		#print determ
		
		logdenom = -.5*len(mu) * log(2*pi) - .5*log(determ)
		pwr = -.5 * transpose(obs - mu) * inv_sig * (obs - mu)
		return (logdenom + pwr)[0,0]

	#The log-likelihood of obs, given this MVGaussian distribution
	#minus the MAXIMUM log-likelihood of this distribution (gaussian_loglik)
	#Effectively normalizes against the "flatness" of distributions with high variance
	#Proportional to gaussian_loglik(obs) - gaussian_loglike(self.mu), but more efficient
	#Params:
		#obs - the observed vector.  Must be an Nx1 Nuumpy matrix (column vector)
		#returns - a scaled log-probability density
	def gaussian_loglik_scaled(self, obs):

		if(self.inv_sig==None):
			return float('-inf')
			
		try:
			(mu, sig, inv_sig, determ, obs) = self.dimension_subset(self.mu, self.sig, obs)
		except InvalidVectorException:
			return 0		

		lnl = -.5 * transpose(obs - mu) * inv_sig * (obs - mu)
		return (lnl)[0,0]
	
	#The expected scaled log-likelihood of this distribution, according to some other distribution
	#Params:
		#otherMu - the mean of the other multivariate gaussian distribution
		#otherSig - the covariance matrix of the other multivariate gaussian distribution
	#Returns: - an expected scaled log-probability density
	def expected_loglik_scaled(self, otherMu, otherSig):
		if(self.inv_sig==None):
			return float('-inf')
		
		
		try:
			(mu, sig, inv_sig, determ, mu2, sig2) = self.dimension_subset(self.mu, self.sig, otherMu, otherSig)
		except InvalidVectorException:
			return 0			
		
		traceterm = -.5 * trace(inv_sig * sig2)
		mahal_term = -.5* transpose(mu - mu2) * inv_sig * (mu - mu2)
		
		return (traceterm + mahal_term)[0,0]
	
	#Using diagonal components of the covariance matrix, compute the z-score for each entry of the vector
	#(obs - mean)/stdev
	#Params:
		# vect - the vector to be standardized
	#Returns: A standardized vector
	def standardize_vector(self, vect):
		tmp = zeros((len(vect), 1))
		for i in range(len(vect)):
			if(vect[i]==0):
				tmp[i] = 0
			else:
				tmp[i] = (vect[i] - self.mu[i]) / sqrt(self.sig[i,i])
		return tmp