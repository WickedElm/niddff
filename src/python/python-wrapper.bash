#!/usr/bin/env bash

##
# A thin wrapper to run python scripts specified in a configuration file.
# All scripts called from this wrapper are expected to have two args:
#   1.  working directory for where to put any output files
#   2.  An input data file to parse as input
###

WORKING_DIR=$1
FEATURES_DIR=$2
SOURCE_FILE_NAME=$3
DATA_FILE=$4
GROUND_TRUTH_FILE=$5

# Parse our features file for use as an input argument
FEATURES_FILE=${FEATURES_DIR}/__load__.python
FEATURES=$(cat ${FEATURES_FILE}  | grep -v "#" | grep -v '^[[:space:]]*$')

if [ ${#FEATURES} -gt 0 ];
then
    for python_script in `echo ${FEATURES}`; do
        echo ""
        echo "Executing [python ${FEATURES_DIR}/${python_script}.py ${WORKING_DIR} ${SOURCE_FILE_NAME} ${DATA_FILE} ${GROUND_TRUTH_FILE}]"
        python ${FEATURES_DIR}/${python_script}.py ${WORKING_DIR} ${SOURCE_FILE_NAME} ${DATA_FILE} ${GROUND_TRUTH_FILE}
    done
fi
