#!/usr/bin/env python

# ----------------------------------------------------------------------------
# A Benchmark Dataset and Evaluation Methodology for Video Object Segmentation
#-----------------------------------------------------------------------------
# Copyright (c) 2016 Federico Perazzi
# Licensed under the BSD License [see LICENSE for details]
# Written by Federico Perazzi
# ----------------------------------------------------------------------------

"""
Display name,title,authors,etc... of available techniques"

EXAMPLE:
	python tools/list_techniques.py

"""

import yaml
import json

from davis    import cfg
from easydict import EasyDict as edict

from davis.dataset import db_read_techniques
from prettytable import PrettyTable as ptable

if __name__ == '__main__':

	# Load techniques
	db_techniques = db_read_techniques()

	# Fill table
	table = ptable(["Abbr","Title","Authors","Conf","Year"])
	for t in db_techniques:
		table.add_row([t.name,t.title,t.authors[0], t.conference,t.year])

	# Print results
	table.align='l'
	print table
