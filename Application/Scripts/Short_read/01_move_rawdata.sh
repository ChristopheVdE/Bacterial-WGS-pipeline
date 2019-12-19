#!/bin/bash

###################################################################################
#NAME SCRIPT: 01_move_rawdata.sh
#AUTHOR: Christophe Van den Eynde  
#copying rawdata to the current analysis data folders
#USAGE: ./01_move_rawdata.sh ${input} ${output}
###################################################################################

#FILE PREPARATION------------------------------------------------------------------
#Fix possible EOL errors in files to read
dos2unix -q /home/rawdata/sampleList.txt
#----------------------------------------------------------------------------------

# copy the 00_Rawdata into the current analysis folder
echo -e "\nMoving files, please wait"
for id in `cat /home/rawdata/sampleList.txt`; do
    mkdir -p /home/rawdata/${id}/00_Rawdata
    cp -vrn /home/rawdata/${id}*.fastq.gz /home/rawdata/${id}/00_Rawdata/ \
    2>&1 | tee -a /home/rawdata/${id}/00_Rawdata/stdout.txt
done    
echo -e "Done\n"