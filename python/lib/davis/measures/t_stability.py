#% [T, raw_results] =  t_stability( object, ground_truth )
#% ------------------------------------------------------------------------
#% Jordi Pont-Tuset - http://jponttuset.github.io/
#% April 2016
#% ------------------------------------------------------------------------
#% This file is part of the DAVIS package presented in:
#%   Federico Perazzi, Jordi Pont-Tuset, Brian McWilliams,
#%   Luc Van Gool, Markus Gross, Alexander Sorkine-Hornung
#%   A Benchmark Dataset and Evaluation Methodology for Video Object Segmentation
#%   CVPR 2016
#% Please consider citing the paper if you use this code.
#% ------------------------------------------------------------------------
#% Calculates the temporal stability index between two masks
#% ------------------------------------------------------------------------
#% INPUT
#%         object      Object mask.
#%   ground_truth      Ground-truth mask.
#%
#% OUTPUT
#%              T      Temporal (in-)stability
#%    raw_results      Supplemental values
#% ------------------------------------------------------------------------

import cv2
import sys
import numpy as np
import scipy.spatial.distance as ssd
from tstab import *
import time

def get_bijective_pairs(pairs,costmat):
	bij_pairs = bij_pairs_one_dim(pairs, costmat,0)
	bij_pairs = bij_pairs_one_dim(bij_pairs, costmat.T,1)
	return bij_pairs

def bij_pairs_one_dim(pairs, costmat, left_or_right):

	bij_pairs = []
	ids1      = np.unique(pairs[:,left_or_right])

	for ii in range(len(ids1)):
		curr_pairs = pairs[pairs[:,left_or_right]==ids1[ii],:].astype(np.int)
		curr_costs = costmat[curr_pairs[:,left_or_right], curr_pairs[:,1-left_or_right]]
		b = np.argmin(curr_costs)
		bij_pairs.append(curr_pairs[b])

	return np.array(bij_pairs)

def hist_cost_2(BH1,BH2):

	nsamp1,nbins=BH1.shape
	nsamp2,nbins=BH2.shape

	eps  = 2.2204e-16
	BH1n = BH1 / (np.sum(BH1,axis=1,keepdims=True)+eps)
	BH2n = BH2 / (np.sum(BH2,axis=1,keepdims=True)+eps)

	tmp1 = np.tile(np.transpose(np.atleast_3d(BH1n),[0,2,1]),(1,nsamp2,1))
	tmp2 = np.tile(np.transpose(np.atleast_3d(BH2n.T),[2,1,0]),(nsamp1,1,1))
	HC = 0.5*np.sum((tmp1-tmp2)**2/(tmp1+tmp2+eps),axis=2)

	return HC


def dist2(x,c):
	ndata,dimx=x.shape
	[ncentres,dimc] = c.shape
	#print  x.T.dot(c).shape

	#print np.ones((ncentres,1)).shape
	#print np.sum((x**2).T,axis=1
	print "c:",c.shape
	print "x:",x.shape

	n2 = np.ones((ncentres,1)).dot(np.sum((x**2).T,axis=0,keepdims=True)).T
	n1 = np.ones((ndata,1)).dot(np.sum((c**2).T,axis=0,keepdims=True))
	n0 = 2 * x.dot(c.T)

	return n1 + n2 -n0


	#print n2.shape,n1.shape

def sc_compute(Bsamp,Tsamp,mean_dist,nbins_theta,nbins_r,r_inner,r_outer,out_vec):
	in_vec = (out_vec==0).ravel()
	nsamp = Bsamp.shape[1]
	r_array=ssd.squareform(ssd.pdist(Bsamp.T)).T
	#r_array_matlab = read_matlab_matrix('/tmp/r_array',',')

	# DEBUGGING
	#r_array = r_array_matlab

	theta_array_abs0=Bsamp[1,:].reshape(-1,1).dot(np.ones((1,nsamp))) - \
			np.ones((nsamp,1)).dot(Bsamp[1,:].reshape(1,-1))

	theta_array_abs1=Bsamp[0,:].reshape(-1,1).dot(np.ones((1,nsamp))) - \
			np.ones((nsamp,1)).dot(Bsamp[0,:].reshape(1,-1))

	theta_array_abs = np.arctan2(theta_array_abs0,theta_array_abs1).T
	theta_array=theta_array_abs-Tsamp.T.dot(np.ones((1,nsamp)))

	if mean_dist is None:
		mean_dist = np.mean(r_array[in_vec].T[in_vec].T)

	r_array_n = r_array / mean_dist

	r_bin_edges=np.logspace(np.log10(r_inner),np.log10(r_outer),nbins_r)
	r_array_q=np.zeros((nsamp,nsamp))
	for m in range(int(nbins_r)):
		r_array_q=r_array_q+(r_array_n<r_bin_edges[m])

	fz = r_array_q > 0
	theta_array_2 = np.fmod(np.fmod(theta_array,2*np.pi)+2*np.pi,2*np.pi)
	theta_array_q = 1+np.floor(theta_array_2/(2*np.pi/nbins_theta))

	nbins=nbins_theta*nbins_r
	BH=np.zeros((nsamp,nbins))
	count = 0
	for n in range(nsamp):
		fzn=fz[n]&in_vec
		Sn = np.zeros((nbins_theta,nbins_r))
		coords = np.hstack((theta_array_q[n,fzn].reshape(-1,1),
			r_array_q[n,fzn].astype(np.int).reshape(-1,1)))

		# SLOW...
		#for i,j in coords:
			#Sn[i-1,j-1] += 1

		# FASTER
		ids = np.ravel_multi_index((coords.T-1).astype(np.int),Sn.shape)
		Sn  = np.bincount(ids.ravel(),minlength = np.prod(Sn.shape)).reshape(Sn.shape)


		BH[n,:] = Sn.T[:].ravel()

	return BH.astype(np.int),mean_dist

def read_matlab_matrix(filename,delimiter):
	with open(filename) as f:
		return np.array([[float(x) for x in line.rstrip().split(delimiter)] for line in f.readlines()])

def t_stability(foreground_mask,ground_truth):
	# Parameters

	cont_th = 3
	cont_th_up = 3

	# Shape context parameters
	r_inner     = 1.0/8.0
	r_outer     = 2.0
	nbins_r     = 5.0
	nbins_theta = 12.0

	poly1 = mask2poly(foreground_mask         ,cont_th)
	poly2 = mask2poly(ground_truth,cont_th)

	if len(poly1.contour_coords) == 0 or \
			len(poly2.contour_coords) == 0:
		return np.nan,[]

	Cs1 = get_longest_cont(poly1.contour_coords)
	Cs2 = get_longest_cont(poly2.contour_coords)

	upCs1 = contour_upsample(Cs1,cont_th_up)
	upCs2 = contour_upsample(Cs2,cont_th_up)

	upCs1_matlab = read_matlab_matrix("/tmp/upCs1",',')
	upCs2_matlab = read_matlab_matrix("/tmp/upCs2",',')

	print np.allclose(upCs1,upCs1_matlab,rtol=0,atol=1e-2)
	print np.allclose(upCs2,upCs2_matlab,rtol=0,atol=1e-2)


	scs1,_=sc_compute(upCs1_matlab.T,np.zeros((1,upCs1.shape[0])),None,
			nbins_theta,nbins_r,r_inner,r_outer,np.zeros((1,upCs1.shape[0])))

	scs2,_=sc_compute(upCs2.T,np.zeros((1,upCs2.shape[0])),None,
			nbins_theta,nbins_r,r_inner,r_outer,np.zeros((1,upCs2.shape[0])))

	scs1_matlab = read_matlab_matrix("/tmp/scs1",',').astype(np.int)
	scs2_matlab = read_matlab_matrix("/tmp/scs2",',').astype(np.int)

	print np.isclose(np.sum(scs1 - scs1_matlab),0)
	print np.isclose(np.sum(scs2 - scs2_matlab),0)

	# Match with the 0-0 alignment
	costmat        = hist_cost_2(scs1,scs2)
	costmat_matlab = read_matlab_matrix('/tmp/costmat',',')

	print np.allclose(costmat_matlab,costmat,rtol=0,atol=1e-2)
	print costmat_matlab.shape

	pairs_matlab         = read_matlab_matrix('/tmp/pairs',',')
	pairs ,max_sx,max_sy = match_dijkstra(np.ascontiguousarray(costmat_matlab))
	print np.allclose(pairs+1,pairs_matlab)


	# Shift costmat
	costmat2 = np.roll(costmat ,-(max_sy+1),axis=1)
	costmat2 = np.roll(costmat2,-(max_sx+1),axis=0)

	costmat2_matlab = read_matlab_matrix('/tmp/costmat2',',')
	print np.allclose(costmat2_matlab,costmat2,rtol=0,atol=1e-2)


	# Redo again with the correct alignment
	pairs,_,_ = match_dijkstra(costmat2_matlab)

	pairs_matlab   = read_matlab_matrix('/tmp/pairs2',',')
	print np.allclose(pairs+1,pairs_matlab)

	# Put the pairs back to the original place
	pairs[:,0] = np.mod(pairs[:,0]+max_sx+1, costmat.shape[0])
	pairs[:,1] = np.mod(pairs[:,1]+max_sy+1, costmat.shape[1])

	pairs_mod_matlab = read_matlab_matrix('/tmp/pairs_mod',',')
	print np.allclose((pairs+1).astype(np.int),pairs_mod_matlab.astype(np.int))


	pairs = get_bijective_pairs(pairs,costmat_matlab)
	pairs_bji_matlab = read_matlab_matrix('/tmp/pairs_bij',',')
	print pairs.shape,pairs_bji_matlab.shape
	print np.allclose((pairs+1).astype(np.int),pairs_bji_matlab.astype(np.int))
	#for p in pairs:
		#print p
	#sys.exit(0)

	#sys.exit(0)

	pairs_cost = costmat_matlab[pairs[:,0], pairs[:,1]]
	min_cost   = np.average(pairs_cost)

	return min_cost



#%% Polygons and shape context
#% To polygonal contour encoding
#poly1 = mask2pce(object      ,cont_th)
#poly2 = mask2pce(ground_truth,cont_th)

#% If one of the masks is empty, return NaN
#% (it will be ignored afterwards in the computation)
#if isempty(poly1.paths) || isempty(poly2.paths)
    #T = NaN
    #raw_results = []
    #return
#end

#% Keep the longest closed contour <-- Can we put everything in one?
#Cs1 = get_longest_cont(poly1)
#Cs2 = get_longest_cont(poly2)

#% Resample so that there are not too long lines
#upCs1 = contour_upsample(Cs1, cont_th_up)
#upCs2 = contour_upsample(Cs2, cont_th_up)

#% 'Classical' shape context
#nsamp1 = size(upCs1,1)
#scs1 = sc_compute(upCs1',zeros(1,nsamp1),[],nbins_theta,nbins_r,r_inner,r_outer,zeros(1,nsamp1))
#nsamp2 = size(upCs2,1)
#scs2 = sc_compute(upCs2',zeros(1,nsamp2),[],nbins_theta,nbins_r,r_inner,r_outer,zeros(1,nsamp2))

#% Compute cost matrix between pairs of points
#costmat = hist_cost_2(scs1,scs2)

#%% Match contours
#% Match with the 0-0 alignment
#[~, max_sx, max_sy] = mex_match_dijkstra( costmat )

#% Shift costmat
#costmat2 = circshift(costmat,[-max_sx,-max_sy])

#% Redo again with the correct alignment
#pairs = mex_match_dijkstra( costmat2 )

#% Put the pairs back to the original place
#pairs(:,1) = mod(pairs(:,1)+max_sx-1, size(costmat,1))+1
#pairs(:,2) = mod(pairs(:,2)+max_sy-1, size(costmat,2))+1

#% Get a bijective matching
#%(could be done by adding zero-cost connections in the graph)
#pairs = get_bijective_matching(pairs, costmat)

#% Get cost of each matching
#pairs_cost = costmat(sub2ind(size(costmat), pairs(:,1), pairs(:,2)))
#min_cost   = sum(pairs_cost)

#%% Compute distance
#% % Estimate the best (affine) transformation
#% [all_dist1,all_dist2,coords2_trans] = segment_dist(upCs1,upCs2,pairs,0)
#%
#% % Compute the distance between all paired (transformed) points
#% pt_from = upCs1(pairs(:,1),:)
#% pt_to	= coords2_trans(pairs(:,2),:)
#% all_d   = sqrt((pt_from(:,1)-pt_to(:,1)).^2+(pt_from(:,2)-pt_to(:,2)).^2)

#%% Save auxiliar results
#raw_results.poly1      = poly1
#raw_results.poly2      = poly2
#raw_results.Cs1        = Cs1
#raw_results.Cs2        = Cs2
#raw_results.upCs1      = upCs1
#raw_results.upCs2      = upCs2
#raw_results.scs1       = scs1
#raw_results.scs2       = scs2
#raw_results.costmat    = costmat
#raw_results.pairs      = pairs
#raw_results.min_cost   = min_cost
#raw_results.pairs_cost = pairs_cost
#% raw_results.upCs2_tran = coords2_trans
#% raw_results.all_d_matched = all_d
#% raw_results.all_d_dist1 = all_dist1
#% raw_results.all_d_dist2 = all_dist2

#%% Compute final value of the measure
#T = raw_results.min_cost/size(raw_results.pairs_cost,1)

#end

def db_eval_t_stab(foreground_mask,ground_truth,timing=True):
	# Parameters

	cont_th = 3
	cont_th_up = 3

	# Shape context parameters
	r_inner     = 1.0/8.0
	r_outer     = 2.0
	nbins_r     = 5.0
	nbins_theta = 12.0

	et = time.time()
	poly1 = mask2poly(foreground_mask,cont_th)
	print "mask2poly: %.5f secs"%(time.time()-et)
	poly2 = mask2poly(ground_truth,cont_th)

	if len(poly1.contour_coords) == 0 or \
			len(poly2.contour_coords) == 0:
		return np.nan,[]

	et = time.time()
	Cs1 = get_longest_cont(poly1.contour_coords)
	print "get_longest_cont: %.5f secs"%(time.time()-et)
	Cs2 = get_longest_cont(poly2.contour_coords)

	et = time.time()
	upCs1 = contour_upsample(Cs1,cont_th_up)
	print "contour_upsample: %.5f secs"%(time.time()-et)
	upCs2 = contour_upsample(Cs2,cont_th_up)

	et = time.time()
	scs1,_=sc_compute(upCs1.T,np.zeros((1,upCs1.shape[0])),None,
			nbins_theta,nbins_r,r_inner,r_outer,np.zeros((1,upCs1.shape[0])))
	print "sc_compute: %.5f secs"%(time.time()-et)

	scs2,_=sc_compute(upCs2.T,np.zeros((1,upCs2.shape[0])),None,
			nbins_theta,nbins_r,r_inner,r_outer,np.zeros((1,upCs2.shape[0])))

	# Match with the 0-0 alignment
	et = time.time()
	costmat              = hist_cost_2(scs1,scs2)
	print "hist_cost_2: %.5f secs"%(time.time()-et)
	et = time.time()
	pairs ,max_sx,max_sy = match_dijkstra(np.ascontiguousarray(costmat))
	print "match_dijkstra: %.5f secs"%(time.time()-et)


	# Shift costmat
	costmat2 = np.roll(costmat ,-(max_sy+1),axis=1)
	costmat2 = np.roll(costmat2,-(max_sx+1),axis=0)

	# Redo again with the correct alignment
	et = time.time()
	pairs,_,_ = match_dijkstra(costmat2)
	print "match_dijkstra: %.5f secs"%(time.time()-et)

	# Put the pairs back to the original place
	pairs[:,0] = np.mod(pairs[:,0]+max_sx+1, costmat.shape[0])
	pairs[:,1] = np.mod(pairs[:,1]+max_sy+1, costmat.shape[1])

	et = time.time()
	pairs = get_bijective_pairs(pairs,costmat)
	print "get_bijective_pairs: %.5f secs"%(time.time()-et)

	pairs_cost = costmat[pairs[:,0], pairs[:,1]]
	min_cost   = np.average(pairs_cost)

	return min_cost

#gt_filename = '../../davis-release/data/davis/Annotations/480p/blackswan/00010.png'
#filename    = '../../davis-release/data/davis/Results/Segmentations/480p/fcp/blackswan/00010.png'

#ground_truth = cv2.imread(gt_filename,0)
#segmentation = cv2.imread(filename,0)

#print t_stability(segmentation,ground_truth)


