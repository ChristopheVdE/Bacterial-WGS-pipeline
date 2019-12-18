#!/bin/bash

###################################################################################
#NAME SCRIPT: 02_move_rawdata.sh
#AUTHOR: Christophe Van den Eynde  
#deletes rawdata files in the main folder (rawdata/) if rawdata and results folder is the same (keeps the rawdata in rawdata/sample/00_rawdata)
#USAGE: ./02_delete_rawdata.sh ${input} ${output}
###################################################################################

#FILE PREPARATION------------------------------------------------------------------
#Fix possible EOL errors in files to read
dos2unix /home/rawdata/sampleList.txt
#----------------------------------------------------------------------------------

# copy the 00_Rawdata into the current analysis folder
echo -e "\nRemoving duplicate rawdata files, please wait"
for id in `cat /home/rawdata/sampleList.txt`; do
    rm /home/rawdata/${id}*.fastq.gz
done    
echo -e "Done\n"