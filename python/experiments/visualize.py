#!/usr/bin/env python

# ----------------------------------------------------------------------------
# The 2017 DAVIS Challenge on Video Object Segmentation
#-----------------------------------------------------------------------------
# Copyright (c) 2017 Federico Perazzi
# Licensed under the BSD License [see LICENSE for details]
# Written by Federico Perazzi
# ----------------------------------------------------------------------------

"""
Visualize sequence annotations.

EXAMPLE:
    python tools/visualize.py

"""


import prettytable
from davis import DAVISLoader,DAVISResults,phase
from davis.dataset.sequence import Sequence
import skimage.io as io
import argparse
import cv2

def parse_args():
	"""Parse input arguments."""

	parser = argparse.ArgumentParser(
			description="Visualize dataset annotations.")

	parser.add_argument(
			'--year',default='2017',type=str,choices=['2016','2017'],
      help='Select dataset year.'
      )

	parser.add_argument(
			'--phase',default=phase.TRAIN,type=str,
      help='Select dataset split.'
      )

	args = parser.parse_args()

	return args

if __name__ == '__main__':
  args = parse_args()

  db = DAVISLoader(
      phase=args.phase,
      year=args.year)

  for sequence in db:
    for im in sequence.visualize(sequence.annotations):
      cv2.imshow("Sequence",im[...,[2,1,0]])
      cv2.waitKey()
      break
