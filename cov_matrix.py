# -*- coding: utf-8 -*-
"""
Created on Wed May 21 17:38:31 2014

@author: brian
"""
from numpy import concatenate, cov, var, matrix, diag, transpose, zeros, mean, trace
from numpy.linalg import inv, det, eig
from math import log, pi, sqrt, exp
from random import random
#from MetropolisHastings import *
from tools import *

class InvalidVectorException(Exception):
	pass

class InvalidCovarianceException(Exception):
	pass

#Represents a multivariate Gaussian distribution.  Likelihood can be evaluated in several ways
class MVGaussian():
	#Initializes the distribution from the given parameters
	#Params:
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
			raise InvalidCovarianceException()
		self.determ = det(sig)
		if(self.determ < 0):
			#print ("Negative determinant")
			raise InvalidCovarianceException()
		
		vals, vects = eig(self.sig)
		for v in vals:
			if(v < 0):
				#print ("Not positive definite")
				raise InvalidCovarianceException()
	def copy(self):
		other = MVGaussian()
		other.mu = self.mu
		other.sig = self.sig
		other.inv_sig = self.inv_sig
		other.determ = self.determ
		return other
		
	@staticmethod
	def mix(mvg1, mvg2, mixing_coef):
		mu = mvg1.mu * mixing_coef + mvg2.mu * (1 - mixing_coef)
		sig = mvg1.sig * mixing_coef + mvg2.sig * (1 - mixing_coef)
		return MVGaussian(mu, sig)
		
	
	#If an observation has missing values, we need to take a subset of the dimensions
	#AKA the mean vector now has less than N dimensions, and the cov matrix is <N x <N
	#This method performs the dimension selection
	#Params:
		#mu - the original N-dimensional mean vector
		#sig - the original NxN covariance matrix
		#obs - the observation which may have some missing values (0 is assumed to be missing)
		#returns a tuple containing the selection on these three inputs, as well as the inverse and determinant of the new matrix
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
		

#Uses a small number of parameters to generate the full covariance matrix
#These parameters indicate the correlations between REGIONS instead of TRIPS (pairs of regions)
#It is assumed that the correlation between trips is the geometric mean of correlations between start regions and end regions
#For example E->M and N->U have the same correlation as M->E and U->N
#Params:
	#diagVar - a list of the diagonal entries of the covariance matrix - the individual variances of trips
	#params - a list containing the parameter values.  Must be ordered lexicographically
	#returns - the generated covariance matrix
def generateParameterizedCovariance(diagVar, params):
	#start with a matrix of all zeros
	cMatrix = zeros(shape=(len(diagVar), len(diagVar)))
	nRegions = int(sqrt(len(params)))
	
	
	#It is more convenient to think of these parameters as a 2D array than a 1D array
	#Use the lexicographic order to split it
	p = [params[i:i+nRegions] for i in range(0,len(params),nRegions)]
	
	#Matrix should be symmetric - discard half of the parameters and replace them with the other half
	for i in range(len(p)):
		for j in range(0,i):
			p[j][i] = p[i][j]


	#Iterate through pairs of trips
	for i in range(len(diagVar)):
		for j in range(len(diagVar)):
			if(i==j):
				#Use the emperical values for diagonal entries
				cMatrix[i,j] = diagVar[i]
			else:
				#Use the lexicographical ordering to determine the start and end regions of trip 1
				start1 = int(i / nRegions)
				end1 = i % nRegions
				#Use the lexicographical ordering to determine the start and end regions of trip 2
				start2 = int(j / nRegions)
				end2 = j % nRegions
				
				#The correlation is the geometric mean of these two terms
				cor = sqrt(p[start1][start2] * p[end1][end2])
				
				#Use diagonal entries to convert correlation to covariance
				#COV(a,b) = COR(a,b) * sqrt(VAR(a) * VAR(b))
				cMatrix[i,j] = cor * sqrt(diagVar[i] * diagVar[j])
	#Return the computed matrix		
	return cMatrix

	
#The likelihood of observing the data, given a set of parameters
#This is the function to be maximized when obtaining the parameters' MLE
#Params:
	#params - the parameters which can be used to construct a covariance matrix via generateParameterizedCovariance()
	#args - additional arguments needed to compute likelihood  breaks down into:
		#mu - the mean of the multivariage gaussian distribution
		#diagVar - the diagonal entries of the covariance matrix
		#data - the list of observed vectors
	#returns - the computed log-likelihood
def parameterizedLnl(params, args):
	#Unpack the arguments
	[mu, diagVar, data] = args
	
	#All parameters must be in (0,1) - Give the lowest possible likelihood to invalid parameters, so they will not be chosen
	for p in params:
		if(p < 0 or p > 1):
			return float('-inf')
	
	
	#Use the parameters to generate the covariance matrix
	sig = generateParameterizedCovariance(diagVar, params)
	
	#Create the multivariate gaussian distribution
	try:
		mvGauss = MVGaussian(mu, sig)
	except InvalidCovarianceException:
		#Some parameters may yield an invalid covariance matrix (not invertible, negative determinant, or not positive definite)
		#Give the lowest possible likelihood to invalid parameters, so they will not be chosen
		return float('-inf')
	
	#Likelihood is the product of likelihoods of independent observations
	#So log-likelihood is the sum of log-likelihoods
	lnl = 0
	for obs in data:
		lnl += mvGauss.gaussian_loglik(obs)
	
	#Return the total likelihood
	return lnl


#Estimates the unbiased covariance matrix of a set of vectors
#Params:
	#pace_vectors - a list of pace vectors.  These must be Nx1 Numpy matrices (column vectors)
	#returns - a Numpy matrix representing the covariance of these vectors
def estimate_cov_full(pace_vectors):
	#glue the vectors together into a matrix
	data_matrix = concatenate(pace_vectors, axis=1)
	#return the full covariance of these vectors
	return matrix(cov(data_matrix))

#Estimates the unbiased covariance matrix of a set of vectors, assuming that they are independent
#In other words, it assumes that the covariance matrix is diagonal, and simply computes the individual variances of each dimension
#Params:
	#pace_vectors - a list of pace vectors.  These must be Nx1 Numpy matrices (column vectors)
	#returns - a Numpy matrix representing the covariance of these vectors (assuming independence)
def estimate_cov_independent(pace_vectors):
	#glue the vectors together into a matrix
	data_matrix = concatenate(pace_vectors, axis=1)
	
	#This creates a vector which contains the variances of each of the rows
	#ddof=1 : unbiased variance estimate (divide by N-1 instead of N)
	ind_vars = var(data_matrix,axis=1,ddof=1)	
	
	#We have a vector containing the variances of each row - convert this into a diagonal matrix
	cov_matrix = diag(transpose(ind_vars).tolist()[0])
	

	return matrix(cov_matrix)
	



#Estimates a parameterized covariance matrix of a set of pace vectors
#A structure is assummed, which defines correlations between REGIONS, instead of REGION-PAIRS (trips)
#The correlation between two trips is the geometric mean of their start-region correlation and end-region correlation
#Note - this computation is fairly heavy since it involves nonlinear search for the Maximum Likelihood Estimate of these parameters
#Params:
	#pace_vectors - a list of pace vectors.  These must be Nx1 Numpy matrices (column vectors)
	#returns - a Numpy matrix representing the covariance of these vectors (assuming the parameterization discussed above)
def estimate_cov_param(pace_vectors):
	#Compute the mean vector
	mu = matrix(mean(pace_vectors, axis=0))
	
	#Compute the diagonal covariance (independent variances of dimensions)
	data_matrix = concatenate(pace_vectors, axis=1)
	ind_vars = var(data_matrix,axis=1,ddof=1)
	

	#Initial guess: N random numbers in (0,1)	
	initial_guess = [random() for i in range(len(pace_vectors[0]))]
	#result = mcmcMaximize(parameterizedLnl, initial_guess, args=[mu,ind_vars,pace_vectors])
	
	#Use Metropolis-Hastings algorithm to find the MLE of the parameters
	result = mc3Maximize(parameterizedLnl, initial_guess, NUM_ITER=1000, NUM_TRIES=10, NUM_PROCESSORS=5, args=[mu,ind_vars,pace_vectors])
	
	#Use parameters to generate the matrix
	m = generateParameterizedCovariance(ind_vars, result.x)
	#logMsg(result)

	return m

#Gives a shrinkage estimate of the covariance matrix
#A weighted compromise between estimate_cov_full (emperical estimate) and estimate_cov_param (parameterized model estimate)
#Params:
	#pace_vectors - a list of pace vectors.  These must be Nx1 Numpy matrices (column vectors)
	#mix_coef - A number between 0 and 1. How much to trust the emperical estimate vs. the model?
	#	    A value of 1 puts full weight on the emperical estimate, but a value of 0 puts full weight on the parameterized model.
	#returns - a Numpy matrix representing the shrunken covariance matrix of these vectors
def estimate_cov_shrinkage(pace_vectors, mix_coef):
	emp = estimate_cov_full(pace_vectors)
	model = estimate_cov_param(pace_vectors)
	return mix_coef * emp +  (1 - mix_coef) * model
