# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 20:10:23 2014

@author: brian
"""

from mvGaussian import *
from numpy import array_equal

class MVGaussianKernel:
	def __init__(self, obs, spherical_bandwidth=10):
		
		diag_list = [spherical_bandwidth] * len(obs)
		sig = matrix(diag(diag_list))
		
		reference_distribution = MVGaussian(obs[0], sig)
		
		self.distributions = []
		for vect in obs:
			if(allNonzero(vect)):
				distribution = reference_distribution.copy()
				distribution.mu = vect
				self.distributions.append(distribution)
	
	def loglik_scaled(self, obs):

		log_ps = []		
		for dist in self.distributions:			
			if(not array_equal(obs, dist.mu)):
				logprob = dist.gaussian_loglik(obs)
				log_ps.append(logprob)
		
		return addLogs(log_ps) - len(log_ps)


if (__name__=="__main__"):
	pass		