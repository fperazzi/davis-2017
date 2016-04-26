#!/usr/bin/env python

# ----------------------------------------------------------------------------
# A Benchmark Dataset and Evaluation Methodology for Video Object Segmentation
#-----------------------------------------------------------------------------
# Copyright (c) 2016 Federico Perazzi
# Licensed under the BSD License [see LICENSE for details]
# Written by Federico Perazzi
# ----------------------------------------------------------------------------

"""
Evaluate a sequence of DAVIS.

EXAMPLE:
	python tools/eval_all.py

"""

import os.path as osp

from davis         import cfg
from prettytable   import PrettyTable as ptable
from davis.dataset import DAVISAnnotationLoader,DAVISSegmentationLoader

if __name__ == '__main__':

	sequence_name = 'flamingo'

	sourcedir = osp.join(cfg.PATH.SEGMENTATION_DIR,'fcp',sequence_name)

	db_annotation   = DAVISAnnotationLoader(cfg,osp.basename(sourcedir))
	db_segmentation = DAVISSegmentationLoader(
			cfg,osp.basename(sourcedir),osp.dirname(sourcedir))

	J,Jm,Jo,Jt = db_annotation.eval(db_segmentation,'T')

	table = ptable(['Sequence']+['Jm','Jo','Jt'])
	table.add_row([sequence_name]+["{: .3f}".format(f) for f in [Jm,Jo,Jt]])

	print table
