#!/bin/bash

###########################################################################################################
#NAME SCRIPT: 01_copy_rawdata.sh
#AUTHOR: Christophe Van den Eynde  
#copying rawdata to the current analysis data folders
#USAGE: ./01_copy_rawdata.sh ${input} ${output}
###########################################################################################################

#FUNCTION--------------------------------------------------------------------------------------------------
usage() {
	errorcode=" \nERROR -> This script can have only 1 parameter:\n
          1: [OPTIONAL] Run date\n";
	echo ${errorcode};
	exit 1;
}
if [ "$#" -gt 1 ]; then
	usage
fi
echo
#-----------------------------------------------------------------------------------------------------------

#VARIABLES--------------------------------------------------------------------------------------------------
Run="$1"
#-----------------------------------------------------------------------------------------------------------

#FILE PREPARATION-------------------------------------------------------------------------------------------
#Fix possible EOL errors in files to read
dos2unix /home/Pipeline/Hybrid/${Run}/sampleList.txt
#-----------------------------------------------------------------------------------------------------------

# copy the 00_Rawdata into the current analysis folder------------------------------------------------------
echo "\nCopying files, please wait"
for id in `cat /home/Pipeline/Hybrid/${Run}/sampleList.txt`; do
    mkdir -p /home/Pipeline/Hybrid/${Run}/Short_reads/${id}//00_Rawdata
    cp -vrn /home/rawdata/${id}*.fastq.gz /home/Pipeline/Hybrid/${Run}/Short_reads/${id}/00_Rawdata/ \
    2>&1 | tee -a /home/Pipeline/Hybrid/${Run}/Short_reads/${id}/00_Rawdata/stdout.txt
done    
echo "Done\n"