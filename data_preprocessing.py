# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 17:23:32 2015

@author: Brian Donovan (briandonovan100@gmail.com)
"""
from numpy import ravel, where, matrix, square, sqrt, cov, real, transpose, sum
from numpy import column_stack, zeros

from numpy.random import rand as rand_array
from numpy.linalg import inv, eigh, qr
import numpy as np

from functools import partial
from tools import DefaultPool




# Deletes dimensions from a data matrix that have too much missing data.
# Params:
    # data_matrix - a Numpy matrix that contains the data - the columns of this
        # matrix are individual observations, and the rows are variables (i.e. dimensions)
    # perc_missing_allowed - a value between 0 and 1 that tells what fraction of
        # missing data is allowed in a given dimension.
# Returns:
    # a smaller matrix
def remove_bad_dimensions(data_matrix, perc_missing_allowed=.01):
    
    n_vars, n_obs = data_matrix.shape
    print("Full data matrix before cutting: %d x %d" % (n_vars, n_obs))
    
    # Compute the percentage of missing data in each dimension
    # We want to exclude observations where ALL dimensions are missing
    # while computing this percentage
    num_all_missing = ((data_matrix==0).sum(axis=0)==n_vars).sum(axis=1) 
    print("Num observations where ALL data is  missing: %d " % num_all_missing)
    num_missing = ((data_matrix==0).sum(axis=1) - num_all_missing)
    perc_missing = num_missing.astype(float) / (n_obs - num_all_missing)
    
    
    # Select only dimensions that have a low enough percentage
    good_dims = ravel(perc_missing < perc_missing_allowed)
    
    # Return the matrix that has rows corresponding to good dimensions
    smaller_data_matrix = data_matrix[good_dims,:]
    n_vars, n_obs = smaller_data_matrix.shape
    print("Full data matrix after cutting: %d x %d" % (n_vars, n_obs))
    return smaller_data_matrix


# A wrapper for remove_bad_dimensions which works on groups of vectors, but removes
# the SAME dimensions from all of them.
# Params:
    # vectors_grouped - a dictionary which maps some group->id to a list of Numpy
        # column vectors
    # perc_missing_allowed - a value between 0 and 1 that tells what fraction of
        # missing data is allowed in a given dimension.
# Returns:
    # new_vectors_grouped - a dictionary which has the same structure as vectors_grouped
        # but the vectors are smaller
def remove_bad_dimensions_grouped(vectors_grouped, perc_missing_allowed=.01):
    # First, concatenate all pace vectors into one big data matrix (in a reasonable order)
    sorted_keys = sorted(vectors_grouped)
    all_vects = [vect for key in sorted_keys for vect in vectors_grouped[key]]
    big_matrix = column_stack(all_vects)
    
    # Now, remove dimensions that have missing data from the big matrix
    new_big_matrix = remove_bad_dimensions(big_matrix, perc_missing_allowed)
    
    # Finally, reconstruct a dictionary which has the same structure as vectors_grouped,
    # but uses the columns of new_big_matrix instead of big_matrix.  We have to be
    # careful to take the vectors out in the same order that we put them in
    new_vectors_grouped = {}
    i = 0
    for key in sorted_keys:
        group_size = len(vectors_grouped[key])
        start=i
        end=i+group_size
        new_vectors_grouped[key] = [new_big_matrix[:,j] for j in xrange(start, end)]
        
        i = end
    
    return new_vectors_grouped
        
    
    

# Replaces missing observations with their average values.  More specifically,
# if observation i has a missing value in variable j, it will be filled in with
# the average value of variable j (using the other non-missing values to compute
# the average.
# Params:
    # data_matrix - a Numpy matrix that contains the data - the columns of this
        # matrix are individual observations, and the rows are variables (i.e. dimensions)
# Returns:
    # no return value - matrix is edited IN PLACE
def impute_missing_data(data_matrix):
    # First compute the average observation (column vector) using only
    # non-missing data
    row_sums = data_matrix.sum(axis=1)
    counts = (data_matrix!=0).sum(axis=1)
    row_avgs = row_sums / counts    
    
    # Now, find the observations that have missing variables and fill them in
    # with the corresponding averages
    row_ids, col_ids = where(data_matrix==0)
    data_matrix[row_ids, col_ids] = row_avgs[row_ids]



# Scales and centers a data matrix.  Specifically, it subtracts the mean
# observation from all observations, and divides all variables by their standard
# deviation
# Params:
    # data_matrix - a Numpy matrix that contains the data - the columns of this
        # matrix are individual observations, and the rows are variables (i.e. dimensions)
    # reference_matrix - If provided, the mean and standard deviation will be computed
        # from this matrix, and then APPLIED to data_matrix
# Returns:
    # new_matrix - a new scaled matrix of the same size
def scale_and_center(data_matrix, reference_matrix=None, scale=False):
    
    if(reference_matrix==None):
        reference_matrix = data_matrix
    # First compute the average observation (column vector) and subtract from
    # every other observation.
    (n_vars, n_obs) = data_matrix.shape
    
    
    row_sums = reference_matrix.sum(axis=1)
    row_avgs = row_sums / n_obs
    new_matrix = data_matrix - row_avgs
    
    # Also scale each variable by its standard deviation, if desired    
        # Var[X] = sum( (X - mean_x)^2) / N
        # Var[X] = sum( (X - 0)^2) / N  # since we already subtracted the mean
    if(scale):
        sums_of_squares = square(reference_matrix).sum(axis=1)
        row_sds = sqrt(sums_of_squares / n_obs)
        new_matrix /= row_sds
    
    return new_matrix


# A helper method that computes eigenvectors / eigenvalues of a matrix, and then
# sorts them in descending order (The default eig function in Numpy does not
# guarantee that they will be in any particular order)
def sorted_eig(m):
    evals, evects = eigh(m)
    sort_order = evals.argsort()[::-1]
    evals = np.sort(evals)[::-1]
    evects = evects[:,sort_order]
    return evals, evects


# Exctracts the top K principal components from a data matrix in the standard (slow)
# way.  It computes the full covariance matrix and the corresponding eigenvectors
# Params:
    # data_matrix - a Numpy matrix that contains the data - the columns of this
        # matrix are individual observations, and the rows are variables (i.e. dimensions)
    # n_pcs - the deisred number of Principal components
def pca(data_matrix, n_pcs):
    (n_vars, n_obs) = data_matrix.shape
    
    n_pcs = min(n_pcs, n_vars)
    # compute the covariance matrix of the observations
    cov_matrix = matrix(cov(data_matrix))
	
    # compute the spectral decomposition
    eig_vals, eig_vectors = sorted_eig(cov_matrix)
    rank = sum(eig_vals > .0001)
    print ("Nonzero eigvals: %d" % rank)
    trunc_eigs = eig_vals.tolist()[:(rank+5)]
    print "Eigen vals: " + str(trunc_eigs)
    eig_ratios = [trunc_eigs[i] / trunc_eigs[i+1] for i in range(len(trunc_eigs)-1)]
    print "Eigen ratios: " + str(eig_ratios)
    print
    
    
    eig_vectors = matrix(eig_vectors)
    principal_components = real(eig_vectors[:,:n_pcs])
    projected_data = transpose(principal_components) * data_matrix
    
    return principal_components, projected_data 


# Extracts the top K principal components from a data matrix, using the iterative
# approach explained in "EM Algorithms for PCA and SPCA, by Sam Roweis".  If the
# number of Principal Components is relatively small, this is more efficient than
# the traditional approach because we don't need to compute the full covariance
# matrix.
# Params:
    # data_matrix - a Numpy matrix that contains the data - the columns of this
        # matrix are individual observations, and the rows are variables (i.e. dimensions)
    # n_pcs - the deisred number of Principal components
def em_pca(data_matrix, n_pcs, tolerance=.000001):
    [n_vars, n_obs] = data_matrix.shape
    
    # Start with an initial guess for the loadings matrix (or eigenvectors)
    loadings = matrix(rand_array(n_vars, n_pcs))
    
    prev_err = float("inf")
    while(True):
        # E-STEP - compute new scores based on current loadings
        # a.k.a. compute projected data based on current eigenvectors
        proj_data = inv(loadings.transpose() * loadings) * loadings.transpose() * data_matrix
    
        # M-STEP - compute new loadings based on current scores
        # a.k..a. compute best eigenvectors based on current projected data
        loadings = data_matrix * proj_data.transpose() * inv(proj_data * proj_data.transpose())
        
        # Compute the squared error
        error = square(data_matrix - loadings * proj_data).sum()
        
        # If the error is no longer decreasing, then we have converged
        error_ratio = error / prev_err
        print(error_ratio)
        if (error_ratio > (1 - tolerance)):
            break
        prev_err = error

    # Now that the EM algorithm has converged, the loadings span the correct lower-
    # dimensional space, and the data is projected into it.  We now use the regular
    # PCA on this lower-dimensional matrix to finish it off and decorrelate the
    # dimensions
    proj_matrix = inv(loadings.transpose() * loadings) * loadings.transpose()
    proj_data =  proj_matrix * data_matrix
    

    new_cov = cov(proj_data)
    orth_cov, rmat = qr(new_cov)
    del(rmat)
    orth_cov = matrix(orth_cov)
    


    """
    new_pcs, new_projected_data = pca(proj_data, n_pcs)

    print proj_matrix.shape
    print new_pcs.shape
    print new_projected_data.shape
    final_pcs = (new_pcs * proj_matrix).transpose() 
    new_data = final_pcs.transpose() * data_matrix
    """
    
    
    import pdb; pdb.set_trace()
    return final_pcs , new_projected_data




def run_opursuit(pace_group, gamma):
    data_matrix = column_stack(pace_group)
    O = (data_matrix!=0)*1 # Observation matrix - 1 where we have data, 0 where we do not
    L,C,term,n_iter = opursuit(data_matrix, O, gamma)
    
    
    outlier_scores = sqrt(sum(square(C), axis=0))    
    
    return list(outlier_scores)



# Preprocesses a group of pace vectors by removing bad dimensions, scaling and centering,
# and applying Principal Component Analysis
# Params:
    # pace_group - a list of Numpy column vectors to be preprocessed
    # n_pcs - The number of principal components to use for PCA
    # scale - Whether or not to do scaling after centering - see scale_and_center()
def preprocess_group(pace_group, n_pcs=0, scale=True):
    data_matrix = column_stack(pace_group)
    
    scale_and_center(data_matrix, scale)
    pcs, projected_data = pca(data_matrix, n_pcs)
    
    em_pcs, em_projected_data = em_pca(data_matrix, n_pcs)
    import pdb; pdb.set_trace()
        
    
    
    # Split the matrix back into vectors
    new_group = [projected_data[:,i] for i in xrange(len(pace_group))]
    
    return new_group





# Preprocesses many groups of pace vectors by removing bad dimensions, scaling
# and centering, and applying PCA.  Some of this preprocessing can be done in parallel
# for each group.
# Params:
    # pace_grouped - The data to be preprocessed.  Should bea dictionary which
        # maps group_ids --> lists of Numpy column vectors
    # perc_missing allowed - a number between 0 and 1 showing how much missing
        # data is allowed in a given dimension.  As usual, missing data is marked
        # by the value 0, since a pace of 0 is impossible
    # n_pcs - the number of principal components to extract during PCA
    # scale - whether or not to scale each variable by its standard deviation -
        # see scale_and_center() for more details
    # pool - An optional multiprocessing.Pool if parallel processing is desired
def preprocess_data(pace_grouped, n_pcs, perc_missing_allowed=.05, scale=True, pool=DefaultPool()):
    
    print(perc_missing_allowed)
    # First, remove the dimensions that have too much missing data.
    pace_grouped = remove_bad_dimensions_grouped(pace_grouped, perc_missing_allowed)
    
    
    # Now, prepare the preprocess_group() function to be mapped onto the groups
    # by "freezing" the other parameters
    #preprocessing_func = partial(preprocess_group, n_pcs=n_pcs, scale=scale)
    preprocessing_func = run_opursuit    
    
    # Make the pace groups into a list instead of a dictionary so they can be mapped
    sorted_keys = sorted(pace_grouped)
    pace_groups = [pace_grouped[key] for key in sorted_keys]
    
    
    # Perform the preprocessing on all groups - if pool is a multiprocessing Pool,
    # this will be done in parallel
    processed_groups = pool.map(preprocessing_func, pace_groups)
    
    # Create a new dictionary which has the same structure as pace_grouped, but with
    # the preprocessed vectors output by preprocess_group()
    new_pace_grouped = {}
    for i in xrange(len(sorted_keys)):
        new_pace_grouped[sorted_keys[i]] = processed_groups[i]
    
    return new_pace_grouped
    
    
    
        
