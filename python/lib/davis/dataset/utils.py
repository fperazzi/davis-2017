# ----------------------------------------------------------------------------
# A Benchmark Dataset and Evaluation Methodology for Video Object Segmentation
#-----------------------------------------------------------------------------
# Copyright (c) 2016 Federico Perazzi
# Licensed under the BSD License [see LICENSE for details]
# Written by Federico Perazzi
# ----------------------------------------------------------------------------

import glob
import h5py
import yaml

import numpy   as np
import os.path as osp

from easydict        import EasyDict as edict
from davis.parallel  import Parallel,delayed
from collections     import defaultdict,OrderedDict

from davis  import cfg
from loader import DAVISAnnotationLoader,DAVISSegmentationLoader

def db_statistics(per_frame_values):

	""" Compute mean,recall and decay from per-frame evaluation.

	Arguments:
		per_frame_values (ndarray): per-frame evaluation

	Returns:
		M,O,D (float,float,float):
			return evaluation statistics: mean,recall,decay.
	"""

	# strip off nan values
	M = np.nanmean(per_frame_values)
	O = np.nanmean(per_frame_values[1:-1]>0.5)

	# Compute decay as implemented in Matlab
	per_frame_values = per_frame_values[1:] # Remove first frame

	N_bins = 4
	#ids = np.round(np.linspace(1, len(per_frame_values),N_bins+1)).astype(np.uint)-1
	ids = np.round(np.linspace(1,len(per_frame_values)-1,N_bins+1)).astype(np.uint)-1;

	D_bins = [per_frame_values[ids[i]:ids[i+1]+1] for i in range(0,4)]
	D      = np.nanmean(D_bins[0])-np.nanmean(D_bins[3])

	return M,O,D

#####################################################
# PERFORM BENCHMARK EVALUATION
#####################################################
def db_eval_sequence(technique,sequence,inputdir):

	""" Perform per-frame sequence evaluation.

	Arguments:
		technique (string): name of the method to be evaluated.
		sequence  (string): name of the sequence to be evaluated.
		inputdir (string): path to the technique folder.

	Returns:
		J,j_M,j_O,j_D: region similarity  (per-frame, mean, recall, decay)
		F,F_M,f_O,f_D: boundary accuracy  (per-frame, mean, recall, decay)
		T,t_M        : temporal stability (per-frame, mean)

	"""

	db_sequence     = DAVISAnnotationLoader(cfg,sequence)
	db_segmentation = DAVISSegmentationLoader(cfg,sequence,
			osp.join(inputdir,technique))

	J,j_M,j_O,j_D = db_sequence.eval(db_segmentation,'J')
	F,f_M,f_O,f_D = db_sequence.eval(db_segmentation,'F')
	T,t_M,_,_     = (np.ones(len(J))*np.nan,np.nan,np.nan,np.nan) # CHANGE

	return  J,j_M,j_O,j_D,F,f_M,f_O,f_D,T,t_M

def db_eval(techniques,sequences,inputdir=cfg.PATH.RESULTS_DIR):

	""" Perform per-frame sequence evaluation.

	Arguments:
		techniques (string,list): name(s) of the method to be evaluated.
		sequences  (string,list): name(s) of the sequence to be evaluated.
		inputdir  (string): path to the technique(s) folder.

	Returns:
		db_eval_dict[method][measure][sequence] (dict): evaluation results.

	"""

	if isinstance(techniques,str): techniques = [techniques]
	if isinstance(sequences,str):  sequences  = [sequences]

	ndict        = lambda: defaultdict(ndict)
	db_eval_dict = ndict()

	# RAW, per-frame evaluation
	for technique in techniques:
		J,j_M,j_O,j_D,F,f_M,f_O,f_D,T,t_M = \
				 zip(*Parallel(n_jobs=cfg.N_JOBS)(delayed(db_eval_sequence)(
			technique,sequence,inputdir) for sequence in sequences))

		# STORE RAW EVALUATION
		for seq_id,sequence in enumerate(sequences):
			db_eval_dict[technique]['J'][sequence] = J[seq_id]
			db_eval_dict[technique]['F'][sequence] = F[seq_id]
			db_eval_dict[technique]['T'][sequence] = T[seq_id]

	return db_eval_dict

#####################################################
# READ DATA
#####################################################
def db_read_properties():
	""" Read dataset properties from file."""
	with open(osp.join(cfg.FILES.DB_INFO),'r') as f:
		return edict(yaml.load(f))

def db_read_benchmark():
	""" Read benchmark data from file."""
	with open(osp.join(cfg.FILES.DB_BENCHMARK),'r') as f:
		return edict(yaml.load(f.read()))

def db_read_sequences():
	""" Read list of sequences. """
	return db_read_properties().sequences

def db_read_techniques():
	""" Read list of benchmarked techniques."""
	return db_read_benchmark().techniques

def db_read_eval(technique=None,measure=None,
		sequence=None,raw_eval=False,inputdir=cfg.PATH.EVAL_DIR):

	""" Read per-frame evaluation from file.

	Arguments:

		technique (string,list): name(s) of the method to be evaluated.
		measure   (string,list): name(s) of measure to be computed (M,O,D).
		sequence  (string,list): name(s) of the sequence to be evaluated.
		inputdir  (string)     : path to the technique(s) folder.
		raw_eval  (bool)       : when False return compute measure statistics (mean,recall,decay).

	Returns:
		db_eval_dict[method][measure][sequence] (dict): evaluation results.

	"""

	def _listify(arg,func):
		if isinstance(arg,str):
			return [arg]
		elif arg is None:
			return func()
		else:
			return arg

	measures   = _listify(measure,
			lambda: db_read_benchmark().measures)

	techniques = _listify(technique,
			lambda: [t.name for t in db_read_techniques()])

	sequences = _listify(sequence,
			lambda: [s.name for s in db_read_sequences()])

	# Compute statistics if not raw_eval else eval_func is is identity
	eval_func = db_statistics \
			if not raw_eval else lambda i:i

	db = {}

	for t in techniques:
		db[t] = OrderedDict()
		db_h5 = h5py.File(osp.join(inputdir,t+'.h5'),'r')

		for m in measures:
			db[t][m] = OrderedDict()
			for s in sequences:
				db[t][m][s] = eval_func(db_h5[m][s][...])

	return db

#######################################################
# SAVE DATA
#######################################################
def db_save_eval(db_eval_dict,outputdir=cfg.PATH.EVAL_DIR):

	""" Save per-frame evaluation to HDF5 file.

	Arguments:
		db_eval_dict[method][measure][sequence] (dict): evaluation results.
		outputdir: destination folder of the output files (one for each technique).

	"""

	for technique in db_eval_dict.keys():
		db_hdf5 = h5py.File(osp.join(outputdir,technique + ".h5"),'w')
		for measure in db_eval_dict[technique].keys():
			for sequence,val in db_eval_dict[technique][measure].iteritems():
				db_hdf5["%s/%s"%(measure,sequence)] = val

		db_hdf5.close()

# HELPER FUNCTION NOT MEANT TO BE USED
def db_save_techniques(db_eval_dict,filename=cfg.FILES.DB_BENCHMARK):

	db_techniques = {'techniques':[],
						 'types'  :['preprocessing','semisupervised','supervised'],
						 'measures':['J','F','T']}

	method_type = [('preprocessing' , ['mcg', 'sf-lab','sf-mot']),
								 ('unsupervised  ', ['nlc', 'cvos', 'trc', 'msg', 'key', 'sal', 'fst']),
								 ('semisupervised', ['tsp', 'sea', 'hvs', 'jmp', 'fcp'])]

	for mtype,techniques in method_type:
		for technique in techniques:
			scores = db_eval_dict[technique]


			def gmr(arg):
				return np.round(np.nanmean(arg.values(),axis=0),3).tolist()

			db_techniques['techniques'].append(
					{
						'name'       : technique,
						'type'       : mtype,
						'J'          : gmr(scores['J']),
						'F'          : gmr(scores['F']),
						'T'          : gmr(scores['T'])
					})

	with open(filename,'w') as f:
		f.write(yaml.dump(db_techniques))
