#!/bin/bash

###################################################################################
#NAME SCRIPT: 01_move_rawdata.sh
#AUTHOR: Christophe Van den Eynde  
#copying rawdata to the current analysis data folders
#USAGE: ./01_move_rawdata.sh ${input} ${output}
###################################################################################

#FUNCTION--------------------------------------------------------------------------------------------------
usage() {
	errorcode=" \nERROR -> This script needs 1 parameters:\n
		1: Analysis type ('short' or 'hybrid')\n";
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 1 ]; then
	usage
fi
echo
#-----------------------------------------------------------------------------------------------------------

#VARIABLES--------------------------------------------------------------------------------------------------
Analysis=$1
#-----------------------------------------------------------------------------------------------------------

#INPUT AND OUTPUT FOLDER------------------------------------------------------------------------------------
if "$Analysis" = "short"; then
	folder="Short_reads"
elif "$Analysis" = "hybrid"; then
	folder="Hybrid/Short_reads"
fi
#-----------------------------------------------------------------------------------------------------------

#FILE PREPARATION-------------------------------------------------------------------------------------------
#Fix possible EOL errors in files to read
dos2unix -q /home/rawdata/${folder}/sampleList.txt
#-----------------------------------------------------------------------------------------------------------

# copy the 00_Rawdata into the current analysis folder
echo "\nMoving files, please wait"
for id in `cat /home/rawdata/${folder}/sampleList.txt`; do
    mkdir -p /home/rawdata/${folder}/${id}/00_Rawdata
    cp -vrn /home/rawdata/${id}*.fastq.gz /home/rawdata/${folder}/${id}/00_Rawdata/ \
    2>&1 | tee -a /home/rawdata/${folder}/${id}/00_Rawdata/stdout.txt
done    
echo "Done\n"