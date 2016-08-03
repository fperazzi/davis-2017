#!/bin/sh

# This scripts downloads the DAVIS data and unzips it.
# Adaptation of a script written in Faster R-CNN (Ross Girshick)

FILE=DAVIS-results.zip
URL=https://graphics.ethz.ch/Downloads/Data/Davis
CHECKSUM=a24f8fa00c955eb7f94ef47ca8d9a62d
DIR=$(pwd)/$(dirname "$0")

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

else
	echo "Checksum is incorrect. Need to download again."
fi

rm -rf $FILE

