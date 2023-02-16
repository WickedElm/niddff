#!/usr/bin/env bash

##
# A thin wrapper around zeek to launch  it
# with an augmented ZEEKPATH.
###

# Get user input zeek packages directory
ZEEK_PACKAGES=$1
shift

WORKING_DIR=$1
shift
cd ${WORKING_DIR}

export SOURCE_FILE_NAME=$1
shift

export DATASET_PACKAGE=$1
shift

# Use zeek with our local packages
zeek --help &> zeek-help
default_zeekpath=$(grep ZEEKPATH zeek-help | awk '{print $6}' | tr -d '(' | tr -d ')')
export ZEEKPATH=$DATASET_PACKAGE:$ZEEK_PACKAGES:$default_zeekpath
rm -f zeek-help

# Run zeek with all remaining arguments
zeek $*

# Save features to a CSV file format
python /niddff/src/zeek/zeek_to_csv.py $SOURCE_FILE_NAME
