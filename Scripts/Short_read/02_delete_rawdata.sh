#!/bin/bash

###########################################################################################################
#NAME SCRIPT: 02_move_rawdata.sh
#AUTHOR: Christophe Van den Eynde  
#deletes rawdata files in the main folder (rawdata/) if rawdata and results folder is the same (keeps the rawdata in rawdata/sample/00_rawdata)
#USAGE: ./02_delete_rawdata.sh ${input} ${output}
###########################################################################################################

#FUNCTION--------------------------------------------------------------------------------------------------
usage() {
	errorcode=" \nERROR -> This script needs 1 parameters:\n
		1: Analysis type\n";
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
elif echo "$Analysis" = "hybrid"; then
	folder="Hybrid/Short_reads"
fi
#-----------------------------------------------------------------------------------------------------------

#FILE PREPARATION-------------------------------------------------------------------------------------------
#Fix possible EOL errors in files to read
dos2unix -q /home/rawdata/${folder}/sampleList.txt
#-----------------------------------------------------------------------------------------------------------

# copy the 00_Rawdata into the current analysis folder
echo -e "\nRemoving duplicate rawdata files, please wait"
for id in `cat /home/rawdata/${folder}/sampleList.txt`; do
    rm /home/rawdata/${id}*.fastq.gz
done    
echo -e "Done\n"