# ----------------------------------------------------------------------------
# A Benchmark Dataset and Evaluation Methodology for Video Object Segmentation
#-----------------------------------------------------------------------------
# Copyright (c) 2016 Federico Perazzi
# Licensed under the BSD License [see LICENSE for details]
# Written by Federico Perazzi
# ----------------------------------------------------------------------------
from config import cfg,set_path_to_cpp_libs
set_path_to_cpp_libs()

from dataset.loader import DAVISAnnotationLoader,DAVISSegmentationLoader

