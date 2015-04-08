# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 19:28:30 2014

@author: Brian Donovan (briandonovan100@gmail.com)
"""
from tools import *
from numpy import transpose, matrix, nonzero, ravel, diag, sqrt, where, square
from numpy import zeros, multiply, column_stack
from numpy.linalg import inv, eig

from data_preprocessing import pca, scale_and_center
from pyrpca_core.op import opursuit




from random import random






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
    
    #If an observation has missing values, we need to take a subset of the dimensions
    #AKA the mean vector now has less than K dimensions where K <= N, and the cov matrix is K x K
    #This method performs the dimension selection
    #Arguments:
        #obs - the observation which may have some missing values (0 is assumed to be missing)
        #returns a tuple containing the selection on these three inputs, as well as the inverse and determinant of the new matrix
    #Returns:
        #A tuple (mean_subset, cov_subset, obs_subset).  Breakdown:
            #mean_subset - a Kx1 vector
            #cov_subset -a KxK matrix
            #obs_subset - a Kx1 vector
    def getIncompleteMeanAndCov(self, obs):
        #First get the full mean and covariance
        (mean, cov) = self.getMeanAndCov()
        
        #Record the indexes with nonzero value
        valid_ids = ravel(nonzero(obs)[0])        
        
        #Perform the selection using Numpy slicing
        mean_subset = mean[valid_ids,:]
        cov_subset = cov[valid_ids,:][:,valid_ids]
        obs_subset = obs[valid_ids]
        
        
        return (mean_subset, cov_subset, obs_subset)        
    
    
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
        if(allNonzero(vect)):
            (mean, cov) = self.getMeanAndCov()
        else:
            (mean, cov, vect) = self.getIncompleteMeanAndCov(vect)
        try:
            mahal = transpose(vect - mean) * inv(cov) * (vect - mean)
            return sqrt(mahal[0,0])
        except:
            print vect
            (vects, vals) = eig(cov)
            print vects
            print vals
    
    #Computes the element-wise standardized vector (zscores)
    #In other words, each dimension of the vector is compared to the corresponding
    #mean and std. dev.
    #params:
        #vect - a Numpy column vector
    #returns:
        #a new Numppy column vector, but with each dimension standardized
    def standardizeVector(self, vect):
        (mean, cov) = self.getMeanAndCov()
        #Extract the diagonal components of the covariance matrix
        #And put them into a column vector
        independent_variances=(transpose(matrix(diag(cov))))
        
        
        

        
        #Note that the division is done element-wise
        std_vector = (vect-mean)/sqrt(independent_variances)
        
        #Deal with missing data properly
        #find the dimensions in the original vector that have missing data
        invalid_ids = where(vect==0)[0]
        #set these values to 0 in the standardized vector (this is how missing data is encoded)
        std_vector[invalid_ids,]=0
        
        return std_vector
    
    







# Represents a set of statistics for a group of mean pace vectors
# Technically, it stores the moments, sum(1), sum(x), sum(x**2)
# Assumes that all elements are uncorrelated - that is, we are extracting
# only the diagonal elements of the covariance matrix
class IndependentGroupedStats:
    # Default constructor.
    # Params:
        # group_of_vectors - a list of Numpy column vectors, on which to compute stats
        # group_of_weights - a list of Numpy column vectors.  Indicates which dimensions
            # will have how much weight for each of the vectors.
    def __init__(self, group_of_vectors, group_of_weights=None):
        #import pdb; pdb.set_trace()
        self.count = 0.0
        self.s_x = 0.0
        self.s_xxt = 0.0
        self.s_w2 = 0.0
        
        if(group_of_weights is None):
            self.weighted = False
        else:
            self.weighted = True
            

        
        #Iterate through mean pace vectors, updating the counts and sums
        for i in xrange(len(group_of_vectors)):
            meanPaceVector = group_of_vectors[i]
            
            if(group_of_weights is None):
                self.s_x += meanPaceVector
                self.s_xxt += square(meanPaceVector)
                self.count += (meanPaceVector!=0)*1
            else:                
                weightVector = group_of_weights[i]
                self.s_x += multiply(meanPaceVector, weightVector)
                self.s_xxt += multiply(square(meanPaceVector), weightVector)
                self.s_w2 += square(weightVector)
                self.count += weightVector
    
    #Make a copy of this GroupedStats object
    #returns: A GroupedStats object, identical to this one
    def copy(self):
        #generate an empty GroupedStats
        cpy = IndependentGroupedStats([])
        
        #copy values from this GroupedStats
        cpy.count = matrix(self.count)
        cpy.s_x = matrix(self.s_x)
        cpy.s_xxt = matrix(self.s_xxt)
        cpy.weighted = self.weighted
        cpy.s_w2 = self.s_w2
        
        #return the copy
        return cpy
    
    #Use the GroupedStats to compute the
    #returns:
        #(mean, cov)  Breakdown:
        #mean - A numpy column vector, representing the mean of all observations
        #var - A numpy column vector, representing the variance of each dimenson of the observations
    def getMeanAndVar(self):
        #E(x) = sum(x) / n
             
        mean = self.s_x / self.count
        
        # Theh unbiased correction is different for the weighted / unweighted cases.
        if(not self.weighted):
            unbiased_correction = self.count / (self.count - 1)
        else:
            unbiased_correction = square(self.count) / (square(self.count) - self.s_w2)
            
        biased_var = (self.s_xxt / self.count) - square(mean)
        var = multiply(biased_var, unbiased_correction) 
        
        return (mean, var)
    
    #If an observation has missing values, we need to take a subset of the dimensions
    #AKA the mean vector now has less than K dimensions where K <= N, and the cov matrix is K x K
    #This method performs the dimension selection
    #Arguments:
        #obs - the observation which may have some missing values (0 is assumed to be missing)
        #returns a tuple containing the selection on these three inputs, as well as the inverse and determinant of the new matrix
    #Returns:
        #A tuple (mean_subset, var_subset, obs_subset).  Breakdown:
            #mean_subset - a Kx1 vector
            #cov_subset -a KxK matrix
            #obs_subset - a Kx1 vector
    def getIncompleteMeanAndVar(self, obs):
        #First get the full mean and covariance
        (mean, var) = self.getMeanAndVar()
        
        #Record the indexes with nonzero value
        valid_ids = ravel(nonzero(obs)[0])        
        
        #Perform the selection using Numpy slicing
        mean_subset = mean[valid_ids,:]
        var_subset = var[valid_ids,:]
        obs_subset = obs[valid_ids]
        
        
        return (mean_subset, var_subset, obs_subset)        
    
    
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
        newStats.count -= (vect!=0)*1
        newStats.s_x -= vect
        newStats.s_xxt -= square(vect)
        return newStats
    
    #Returns the mahalanobis distance of a vector from the mean
    #This is one way of measuring how much of an outlier that vector is
    #params:
        # vector - A numpy column vector to measure
        # feature_weights - A vector of the same size as "vect" that specify weights
            # on individual dimensions.  It is recommended to set normalize=True if
            # feature_weights are used, so the weights can be normalized
        # normalize - if True, mahalanobis will divide by the number of
            # dimensions before taking the square root.  This makes a fairer comparison between
            # cases that do not have the same number of dimensions
    #returns a positive number representing the mahalanobis distance
    def mahalanobisDistance(self, vect, feature_weights = None, normalize=False):
        if(allNonzero(vect) or (feature_weights!=None)):
            (mean, var) = self.getMeanAndVar()
        else:
            (mean, var, vect) = self.getIncompleteMeanAndVar(vect)
        
   
        try:
            if(feature_weights is None):
                mahal = (transpose(vect - mean)) * ((vect - mean) / var)
                if(normalize):
                    mahal /= len(vect)
            else:
                weighted_diff = multiply((vect-mean), feature_weights)
                mahal = (transpose(vect-mean)) * (weighted_diff / var)
                if(normalize):
                    mahal /= sum(feature_weights)
                
                
            
            return sqrt(mahal[0,0])
        except:
            print "%d , %d ???"%(len(vect), sum(square(feature_weights)))
                   
    
    #Computes the element-wise standardized vector (zscores)
    #In other words, each dimension of the vector is compared to the corresponding
    #mean and std. dev.
    #params:
        #vect - a Numpy column vector
    #returns:
        #a new Numppy column vector, but with each dimension standardized
    def standardizeVector(self, vect):
        (mean, var) = self.getMeanAndVar()

        
        #Note that the division is done element-wise
        std_vector = (vect-mean)/sqrt(var)
        
        #Deal with missing data properly
        #find the dimensions in the original vector that have missing data
        invalid_ids = where(vect==0)[0]
        #set these values to 0 in the standardized vector (this is how missing data is encoded)
        std_vector[invalid_ids,]=0
        
        return std_vector
    



"""        
#Computes the mahalanobis distance of each vector from the mean
#Using a leave-one-out estimate.  Also computes the element-wise standardized vector (z-scores)
#params:
    #vectors - a list of Numpy vectors
    #independent - If True, correlations between dimensions will be ignored
        # (i.e. a diagonal covariance matrix will be used)
    # group_of_weights - A list of Numpy Column vectors, indicating feature-by-feature weights
        # for each vector
    # normalize- If True, the Mahalanobis Distance will be divided by the total
        # number of nonzero elements of the vector (or the total weight if weights
        # are given) before the square root is taken.  This ensures a fair comparison
        # between vectors if data is missing or weights have very different magnitudes
#returns:
    # distances - a list of Mahalanobis distances,  correspondign to the input vectors
    # zscores - a list of standardized vectors, corresponding to the input vectors
def computeMahalanobisDistances(vectors, independent=False, group_of_weights=None, normalize=False):
    #compute the groupedStats for the vectors
    if(independent):
        groupedStats = IndependentGroupedStats(vectors, group_of_weights=group_of_weights)
    else:
        groupedStats = GroupedStats(vectors)
    
    distances = []
    zscores = []
    #We want to compute the Mahalanobis distance for each vector
    for i in xrange(len(vectors)):
        # Grab the vector (and the corresponding feature weights if necessary)
        vect = vectors[i]
        if(group_of_weights is None):
            feature_weights = None
        else:
            feature_weights = group_of_weights[i]
            
        #Get the leave-one-out stats
        stats = groupedStats.generateLeave1Stats(vect)
        #stats = groupedStats
        #Use these to compute the mahalanobis distance from this vector, and add to list
        mahalanobisDistance = stats.mahalanobisDistance(vect,
                                                        feature_weights=feature_weights,
                                                        normalize=normalize)
        distances.append(mahalanobisDistance)
        
        #Compute the element-wise standardized vector
        z_vector = stats.standardizeVector(vect)
        zscores.append(z_vector)
        
    #finally, return the computed distances and zscores
    return (distances, zscores)
"""

# Compute the Mahalanobis Distances of a group of vectors in order to quantify
# how unusual they are.  PCA approximation is used for high dimensional data,
# and Robust PCA via Outlier Pursuit is available.
# Params:
    # vectors - a list of Numpy column vectors
    # robust - True if RPCA via OP is desired
    # k - Number of PCs to use in PCA
    # gamma - gamma parameter for RPCA
def computeMahalanobisDistances(vectors, robust=False, k=10, gamma=.5):
    if(robust):
        data_matrix = column_stack(vectors)
        O = (data_matrix!=0)*1 # Observation matrix - 1 where we have data, 0 where we do not
        
        #logMsg("OP")
         # Use outlier pursuit to get robust low-rank approximation of data
        L,C,term,n_iter = opursuit(data_matrix, O, gamma)
        
        #logMsg("PCA")
        # Perform PCA on the low-rank approximation, and estimate the statistics
        scaled_L = scale_and_center(L)
        pcs, robust_lowdim_data = pca(scaled_L, k)
        
        #logMsg("Mahal")
        vects = [robust_lowdim_data[:,i] for i in xrange(robust_lowdim_data.shape[1])]
        stats = IndependentGroupedStats(vects) # Diagonal covariance assumption is valid since we did PCA

        #print("")        
        # Project the original reconstructed data into the low-D space
        # (L+C, which includes the outliers)
        scaled_corrupt = scale_and_center(L+C, reference_matrix=L)
        corrupt_lowdim_data = pcs.transpose() * scaled_corrupt
        
        vects = [corrupt_lowdim_data[:,i] for i in xrange(corrupt_lowdim_data.shape[1])]
        mahals = [stats.mahalanobisDistance(vect) for vect in vects]
        c_vals = [(sum(square(C[:,i]))!=0)*1 for i in  xrange(C.shape[1])]

        return mahals, c_vals
    else:
        pcs, lowdim_data = pca(L, k)
        vects = [lowdim_data[:,i] for i in xrange(lowdim_data.shape[1])]
        stats = IndependentGroupedStats(vects) # Diagonal covariance assumption is valid since we did PCA

        mahals = [stats.generateLeave1stats(vect).mahalanobisDistance(vect) for vect in vects]
        
        return mahals
        









# A helper method for testing purposes.  Randomly generates vectors in [0,1]
# Params:
    # num - how many vectors to create
    # dim - the dimension of vectors to create
    # p_zero - elements of vectors will randomly be set to zero with this probability
def genVectors(num, dim, p_zero):
    vects = []
    for n in range(num):
        vect = matrix(zeros((dim,1)))
        for d in range(dim):
            vect[d,0] = random()
            if(random() < p_zero):
                vect[d,0] = 0
        vects.append(vect)
    return vects

# A simple test case
if(__name__=="__main__"):
    vects = genVectors(1000,1000, 0)
    weights = genVectors(1000,1000, .2)
    
    
    d,z = computeMahalanobisDistances(vects, independent=True, group_of_weights = weights, normalize=True)
    print(d)
    
