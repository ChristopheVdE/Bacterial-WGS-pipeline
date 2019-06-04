#!/bin/bash

###########################################################################################################
#NAME SCRIPT: 01_copy_rawdata.sh
#AUTHOR: Christophe Van den Eynde  
#copying rawdata to the current analysis data folders
#USAGE: ./01_copy_rawdata.sh ${input} ${output}
###########################################################################################################

#FILE PREPARATION-------------------------------------------------------------------------------------------
#Fix possible EOL errors in files to read
dos2unix /home/Pipeline/sampleList.txt
#-----------------------------------------------------------------------------------------------------------

# copy the 00_Rawdata into the current analysis folder------------------------------------------------------
echo "\nCopying files, please wait"
for id in `cat /home/Pipeline/sampleList.txt`; do
    mkdir -p /home/Pipeline/Hybrid/${id}/Short_reads/00_Rawdata
    cp -vrn /home/rawdata/${id}*.fastq.gz /home/Pipeline/Hybrid/${id}/Short_reads/00_Rawdata/ \
    2>&1 | tee -a /home/Pipeline/Hybrid/${id}/Short_reads/00_Rawdata/stdout.txt
done    
echo "Done\n"