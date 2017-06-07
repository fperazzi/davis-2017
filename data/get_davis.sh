#!/bin/sh

# This scripts downloads the DAVIS data and unzip it.

URL=https://data.vision.ee.ethz.ch/jpont/davis

FILE_TRAINVAL=DAVIS-2017-trainval-480p.zip
FILE_TESTDEV=DAVIS-2017-test-dev-480p.zip

if [ ! -f $FILE_TRAINVAL ]; then
  echo "Downloading DAVIS 2017 (train-val)..."
  wget $URL/$FILE_TRAINVAL
else
	echo "File $FILE_TRAINVAL already exists. Checking md5..."
fi

if [ ! -f $FILE_TESTDEV ]; then
  echo "Downloading DAVIS 2017 (test-dev)..."
  wget $URL/$FILE_TESTDEV
else
	echo "File $FILE_TESTDEV already exists. Checking md5..."
fi

unzip -o $FILE_TRAINVAL
unzip -o $FILE_TESTDEV

rm -rf $FILEjTESTDEV $FILE_TRAINVAL
