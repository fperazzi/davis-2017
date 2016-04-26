#!/usr/bin/env python

# ----------------------------------------------------------------------------
# A Benchmark Dataset and Evaluation Methodology for Video Object Segmentation
#-----------------------------------------------------------------------------
# Copyright (c) 2016 Federico Perazzi
# Licensed under the BSD License [see LICENSE for details]
# Written by Federico Perazzi
# ----------------------------------------------------------------------------

import yaml
import json

from davis    import cfg
from easydict import EasyDict as edict

from davis.dataset import db_read_techniques

if __name__ == '__main__':

	db_techniques = db_read_techniques()

	from prettytable import PrettyTable as ptable

	table = ptable(["Abbr","Title","Authors","Conf","Year"])
	table.align='l'
	technique_table = {}
	for t in db_techniques:
		technique_table[t.name]            = edict()
		technique_table[t.name].title      = t.title
		technique_table[t.name].authors    = t.authors
		technique_table[t.name].conference = t.conference
		technique_table[t.name].year       = t.year
		table.add_row([t.name,t.title,t.authors[0], t.conference,t.year])

	with open("techniques.json",'w') as f:
		f.write(json.dumps(technique_table,indent=2))
	print table
