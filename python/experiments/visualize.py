#!/usr/bin/env python

# ----------------------------------------------------------------------------
# The 2017 DAVIS Challenge on Video Object Segmentation
#-----------------------------------------------------------------------------
# Copyright (c) 2017 Federico Perazzi
# Licensed under the BSD License [see LICENSE for details]
# Written by Federico Perazzi
# ----------------------------------------------------------------------------

"""
Visualize segmentation.

EXAMPLE:
    python experiments/visualize.py

"""


import cv2
from   davis import cfg,overlay,DAVISLoader

db = DAVISLoader(year=cfg.YEAR,phase=cfg.PHASE)
im = overlay(db[0].images[0],db[0].annotations[0],db.color_palette)

cv2.imshow("Segmentation",im[...,[2,1,0]])
cv2.waitKey()
