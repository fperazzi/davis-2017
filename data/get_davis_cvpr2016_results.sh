#!/bin/bash

# This scripts downloads the DAVIS data and unzips it.
# Adaptation of a script written in Faster R-CNN (Ross Girshick)

FILE=davis-results-cvpr2016.zip
URL=https://graphics.ethz.ch/Downloads/Data/Davis
CHECKSUM=24e828e81c1bdf1640d2c2ed0fa9de41

if [ ! -f $FILE ]; then
	echo "Downloading DAVIS input (1.9GB)..."
	wget $URL/$FILE

else
	echo "File already exists. Checking md5..."
fi

# CHECKING MDS
os=`uname -s`
if [ "$os" = "Linux" ]; then
	checksum=`md5sum $FILE | awk '{ print $1 }'`
elif [ "$os" = "Darwin" ]; then
	checksum=`cat $FILE | md5`
fi
if [ "$checksum" = "$CHECKSUM" ]; then
	echo "Checksum is correct."
	echo "Unzipping..."
	unzip $FILE

	# Put in folder "davis"
	mkdir -p davis && mv davis-results-cvpr2016/* davis/ && rm -r davis-results-cvpr2016
else
	echo "Checksum is incorrect. Need to download again."
fi

rm -rf $FILE

