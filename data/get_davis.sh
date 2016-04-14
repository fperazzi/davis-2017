#!/bin/bash

# This scripts downloads the DAVIS data and unzips it.
# Adaptation of a script written in Faster R-CNN (Ross Girshick)

FILE=davis-data.zip
URL=https://graphics.ethz.ch/Downloads/Data/Davis
CHECKSUM=bf73a78af1a44706a885f34363b339f1

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
	mkdir -p davis && mv davis-data/* davis/ && rm -r davis-data
else
	echo "Checksum is incorrect. Need to download again."
fi

rm -rf $FILE

