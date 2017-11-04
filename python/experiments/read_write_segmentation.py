#!/usr/bin/env python

# ----------------------------------------------------------------------------
# The 2017 DAVIS Challenge on Video Object Segmentation
#-----------------------------------------------------------------------------
# Copyright (c) 2017 Federico Perazzi
# Licensed under the BSD License [see LICENSE for details]
# Written by Federico Perazzi
# ----------------------------------------------------------------------------

"""
Read and write segmentation in indexed format.

EXAMPLE:
    python experiments/read_write_segmentation.py

"""

import cv2
from   davis import cfg,io,DAVISLoader

# Load dataset
db = DAVISLoader(year=cfg.YEAR,phase=cfg.PHASE)

# Save an annotation in PNG indexed format to a temporary file
io.imwrite_indexed('/tmp/anno_indexed.png',db[0].annotations[0])

# Read an image in a temporary file
an,_ = io.imread_indexed('/tmp/anno_indexed.png')

cv2.imshow("Segmentation",cfg.palette[an][...,[2,1,0]])
cv2.waitKey()
