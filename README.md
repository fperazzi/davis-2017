
A Benchmark Dataset and Evaluation Methodology for Video Object Segmentation (DAVIS)
=====================================================================================

Package containing helper functions for loading and evaluating [DAVIS](https://graphics.ethz.ch/~perazzif/davis/index.html).

Introduction
--------------
DAVIS (Densely Annotated VIdeo Segmentation), consists of fifty high quality,
Full HD video sequences, spanning multiple occurrences of common video object
segmentation challenges such as occlusions, motion-blur and appearance
changes. Each video is accompanied by densely annotated, pixel-accurate and
per-frame ground truth segmentation.

Citation
--------------

Please cite `DAVIS` in your publications if it helps your research:

    `@inproceedings{Perazzi_CVPR_2016,
      author    = {Federico Perazzi and
                   Jordi Pont-Tuset and
                   Brian McWilliams and
                   Luc Van Gool and
                   Markus Gross and
                   Alexander Sorkine-Hornung},
      title     = {A Benchmark Dataset and Evaluation Methodology for Video Object Segmentation},
      booktitle = {The IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
      year      = {2016}
    }`

Terms of Use
--------------
DAVIS is released under the BSD License [see LICENSE for details]

Dependencies
------------
Required:
 * Cython==0.24
 * PyYAML==3.11
 * argparse==1.2.1
 * easydict==1.6
 * future==0.15.2
 * h5py==2.6.0
 * matplotlib==1.5.1
 * numpy==1.11.0
 * prettytable==0.7.2
 * scikit-image==0.12.3
 * scipy==0.17.0

Installation
--------------
1. pip install virtualenv virtualenvwrapper
2. source /usr/local/bin/virtualenvwrapper.sh
3. mkvirtualenv davis
3. pip install -r python/requirements.txt
4. export PYTHONPATH=$(pwd)/python/lib

Documentation
----------------
See source code for documentation.

The directory is structured as follows:

 * `ROOT/python/tools`: contains scripts for evaluating segmentation.
     - `eval.py` : evaluate a technique and store results in HDF5 file
     - `eval_view.py`: read and display evaluation from HDF5.

 * `ROOT/python/experiments`: contains several demonstrative examples.
 * `ROOT/python/lib/davis`  : library package contains helper function for parsing and evaluating DAVIS

 * `ROOT/data` :
		 - `get_davis.sh`: download input images and annotations.
		 - `get_davis_cvpr2016_results.sh`: download the CVPR 2016 submission results.



Contacts
------------------
- [Federico Perazzi](https://graphics.ethz.ch/~perazzif)
- [Jordi Pont-Tuset](http://jponttuset.github.io)
