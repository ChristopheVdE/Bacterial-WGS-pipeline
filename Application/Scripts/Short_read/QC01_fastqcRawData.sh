#!/bin/bash

############################################################################################################
#NAME SCRIPT: runFastqc.sh
#AUTHOR: Tessa de Block
#DOCKER UPDATE: Christophe Van den Eynde
#RUNNING FASTQC
#USAGE: ./runFastqc.sh <number of threads>
############################################################################################################

#VALIDATE NR OF PARAMETERS----------------------------------------------------------------------------------
# parameters are provided by snakefile (hardcoded)
#-----------------------------------------------------------------------------------------------------------

#VARIABLES--------------------------------------------------------------------------------------------------
threads=${1:-"1"}
# inputFolder = /home/Pipeline/${id}/00_Rawdata
# outputFolder = /home/Pipeline/${id}/01_QC_rawdata/QC_FastQC
#-----------------------------------------------------------------------------------------------------------

#FASTQC PRE-START-------------------------------------------------------------------------------------------
#Fix possible EOL errors in sampleList.txt
dos2unix -q /home/Pipeline/sampleList.txt
echo
#-----------------------------------------------------------------------------------------------------------

#RUN FASTQC-------------------------------------------------------------------------------------------------
echo "Starting FastQC with ${threads} threads"
for id in `cat /home/Pipeline/sampleList.txt`; do
     #CREATE OUTPUTFOLDER IF NOT EXISTS
     mkdir -p /home/Pipeline/${id}/01_QC-Rawdata/QC_FastQC
     #RUN FASTQC
     for i in $(ls /home/Pipeline/${id}/00_Rawdata | grep fastq.gz); do
          echo -e "STARTING ${i} \n";
          fastqc --extract \
          -t ${threads} \
          -o /home/Pipeline/${id}/01_QC-Rawdata/QC_FastQC \
          /home/Pipeline/${id}/00_Rawdata/${i} \
          2>&1 | tee -a /home/Pipeline/${id}/01_QC-Rawdata/QC_FastQC/stdout_err.txt ;
          echo -e "\n ${i} FINISHED \n";
     done
done
#------------------------------------------------------------------------------------------------------------

