#!/bin/bash

# This scripts downloads the DAVIS data and unzips it.
# Adaptation of a script written in Faster R-CNN (Ross Girshick)

FILE=davis-results.zip
URL=https://graphics.ethz.ch/Downloads/Data/Davis
CHECKSUM=dc4eefb8a507891938f9867b21d9a1c4

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
	mkdir -p davis && mv ${FILE%.*}/* davis/ && rm -r $FILE
else
	echo "Checksum is incorrect. Need to download again."
fi

rm -rf $FILE ${FILE%.*}

