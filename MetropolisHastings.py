# -*- coding: utf-8 -*-
"""
Created on Fri May 30 09:20:24 2014

@author: brian
"""
from math import exp
from random import random, uniform, gauss
from numpy import matrix
from tools import *
from multiprocessing import Process, Queue



#Randomly perturbs a vector, by independently adding gaussian noise to each entry
#Params:
	#v - the original vector
	#sigma - the standard deviation of the noise distribution
def perturb(v, sigma):
	v2 = list(v)
	for i in range(len(v)):
		#v2[i] = uniform(v[i] - MAX_PERTURB, v[i] + MAX_PERTURB)
		v2[i] = gauss(v[i], sigma)
		if(v2[i] < 0):
			v2[i] = 0
		elif(v2[i] > 1):
			v2[i] = 1
	return v2
	

#The "answer" to a maximization problem
#Contains the arg max input (.x) and the optimum value of the function (.fun)
#Also has a __str__ method for convenient printing
class Answer:
	def __init__(self):
		#Initialize parameters
		self.x = None
		self.fun = None
	def __str__(self):
		
		p = [self.x[i:i+4] for i in range(0,13,4)]
		for i in range(len(p)):
			for j in range(0,i):
				p[j][i] = p[i][j]		
		m = matrix(p)
		
		return "fun:" + str(self.fun) + "  x:\n" + str(m)

#Uses the Metropolis Hastings algorithm to maximize a log-likelihood function (determine the MLE)
#Also makes use of Simulated Annealing - the size of perturbations decays over iterations
#Params:
	#lnlFun - the log-likelihood function to be maximized
	#initialguess - the starting point for the Markov Chain
	#MAX_PERTURB - how much to perturb the current state for the proposal?  Decays over iterations
	#MIN_PERTURB - perturbation size will eventually decay to this on the last iteration
	#NUM_ITER - the number of iterations
def mcmcMaximize(lnlFun, initialguess, MAX_PERTURB=.1, MIN_PERTURB=.002, NUM_ITER=1000, args=[]):
	
	#Evaluate the likelihood function at the initial guess
	currentLnl = lnlFun(initialguess, args)
	while(currentLnl==float('-inf')):
		#If the log-likelihood is -infinity, then the initial guess is not in the feasible set
		#Keep guessing until we find a valid point
		initialguess = [random() for i in range(len(initialguess))]
		currentLnl = lnlFun(initialguess, args)
		
	#The Markov Chain begins at this random start poing
	currentState = initialguess	
	
	#This is the best state so far because it is the only state so far
	bestAnswer = Answer()
	besAnswer.x = currentState
	bestAnswer.fun = currentLnl
	
	energy = 1.0 #Simulated Annealing - start at full energy
	#The cooling rate is defined by the MAX_PERTURB and MIN_PERTURB
	#The perturbation will geometrically decay by cooling_rate each iteration, until it reaches MIN_PERTURB on the last iteration
	cooling_rate = (MIN_PERTURB / MAX_PERTURB) ** (1.0 / NUM_ITER)
	for i in range(NUM_ITER):
		
		
		#Compute the new energy based on the iteration
		energy = cooling_rate**i
		
		#Propose a new state by slightly perturbing the current one
		proposal = perturb(currentState, MAX_PERTURB * energy)
		#Compute the 
		proposalLnl = lnlFun(proposal, args)
		
			
		
		#Some bookkeeping - if the proposal is the best state we have seen so far, save it
		#In this way, we keep track of the maximum
		if(proposalLnl > bestAnswer.fun):
			bestAnswer.x = proposal
			bestAnswer.fun = proposalLnl

		
		#Compute the accptance ratio - the odds ratio of the proposal against the current state P(proposal) / P(current)
		acceptanceRatio = exp(proposalLnl - currentLnl)
		
		#Transation to the new state with this probability
		#Note that if acceptanceRatio > 1 (the proposal is better than the current), we will ALWAYS transition
		if(random() < acceptanceRatio):
			currentState = proposal
			currentLnl = proposalLnl
	
		
	return bestAnswer



#A process which runs mcmcMaximize several times and returns the best answer of any
#The purpose of this class is that many runs of mcmcMaximize can be divided between processes and computed in parallel
class WorkerProcess(Process):
	#Custructor
	#Params:
		#lnlFun - the log-likelihood function to be maximized
		#initialguess - the starting point for the Markov Chain.  Will be randomly overwritten in each iteration - the input value serves as an example
		#MAX_PERTURB - how much to perturb the current state for the proposal?  Decays over iterations
		#MIN_PERTURB - perturbation size will eventually decay to this on the last iteration
		#NUM_ITER - the number of iterations per chain
		#NUM_TRIES - the number of chains to compute (in series - use multiple instances of this class to use parallel)
		#args - additional arguments to the lnlFun
	def __init__(self, lnlFun, initialguess, MAX_PERTURB=.1, MIN_PERTURB=.002, NUM_ITER=1000, NUM_TRIES=1, args=[]):
		super(WorkerProcess, self).__init__()
		self.lnlFun = lnlFun
		self.initialguess = initialguess
		self.MAX_PERTURB = MAX_PERTURB
		self.NUM_ITER = NUM_ITER
		self.NUM_TRIES=NUM_TRIES
		self.args = args
		self.q = Queue()
	
	#Run the process
	def run(self):
		bestAns = None
		#Run N chains, one after another
		for i in range(self.NUM_TRIES):
			#Start with a random guess
			initialguess = [random() for i in range(len(self.initialguess))]
			#Run the maximization
			ans = mcmcMaximize(self.lnlFun, initialguess, self.MAX_PERTURB, self.MIN_PERTURB, NUM_ITER=self.NUM_ITER, args=self.args)
			#Keep track of the best answer so far
			if(bestAns ==None or ans.fun > bestAns.fun):
				bestAns = ans
				
		#Push the answer into the queue, so the calling process can retrieve it
		self.q.put(bestAns)

#Uses the Metropolis Hastings algorithm to maximize a log-likelihood function (determine the MLE)
#Runs multiple chains to ensure mixing, and can make use of parallel processing (run a fixed number of chains on each processor)
#Params:
	#lnlFun - the log-likelihood function to be maximized
	#initialguess - the starting point for the Markov Chain.  Will be randomly overwritten in each iteration - the input value serves as an example
	#MAX_PERTURB - how much to perturb the current state for the proposal?  Decays over iterations
	#MIN_PERTURB - perturbation size will eventually decay to this on the last iteration
	#NUM_ITER - the number of iterations per chain
	#NUM_TRIES - the total number of independent chains to run
	#NUM_PROCESSORS - the number of processors to use for processing these chains.
	#		  Each processor will compute (NUM_TRIES / NUM_PROCESSORS) chains
	#args - additional arguments to the lnlFun
	
def mc3Maximize(lnlFun, initialguess, MAX_PERTURB=.1, MIN_PERTURB = .002, NUM_ITER=1000, NUM_TRIES=10, NUM_PROCESSORS=2, args=[]):
	#Each processor will compute some portion of the chains
	chainsPerProcess = int(floor(NUM_TRIES/NUM_PROCESSORS))
	
	#Create the worker processes
	workers = []
	for i in range(NUM_PROCESSORS):
		
		#How many chains should run on this processor?
		#There is a special case if NUM_TRIES is not divisible by NUM_PROCESSORS
		if(NUM_PROCESSORS * chainsPerProcess + i < NUM_TRIES):
			nTry = chainsPerProcess
		else:
			nTry = chainsPerProcess + 1
		
		#Start the worker and add it to the list
		worker = WorkerProcess(lnlFun, initialguess, MAX_PERTURB=MAX_PERTURB, MIN_PERTURB=MIN_PERTURB, NUM_ITER=NUM_ITER, NUM_TRIES=nTry, args=args)
		worker.start()
		workers.append(worker)
	
	#Once workers are complete, we start receiving answers from their queues
	bestAns = None
	for w in workers:
		#Get the answer, then terminate the process
		ans = w.q.get()
		w.terminate()
		#Keep track of the best answer across processes
		if(bestAns==None or ans.fun > bestAns.fun):
			bestAns = ans
	return bestAns