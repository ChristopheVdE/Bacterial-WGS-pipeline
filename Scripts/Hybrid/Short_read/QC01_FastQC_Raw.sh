#!/bin/bash

############################################################################################################
#NAME SCRIPT: runFastqc.sh
#AUTHOR: Tessa de Block
#DOCKER UPDATE: Christophe Van den Eynde
#RUNNING FASTQC
#USAGE: ./runFastqc.sh <number of threads>
############################################################################################################

#FUNCTION--------------------------------------------------------------------------------------------------
usage() {
	errorcode=" \nERROR -> This script can have only 1 parameter:\n
          1: [OPTIONAL] Ammount of threads to use (default = 1)\n";
	echo ${errorcode};
	exit 1;
}
if [ "$#" -gt 1 ]; then
	usage
fi
echo
#-----------------------------------------------------------------------------------------------------------

#VARIABLES--------------------------------------------------------------------------------------------------
Threads=${1:-"1"}
#-----------------------------------------------------------------------------------------------------------

#FASTQC PRE-START-------------------------------------------------------------------------------------------
#Fix possible EOL errors in sampleList.txt
dos2unix /home/Pipeline/sampleList.txt
echo
#-----------------------------------------------------------------------------------------------------------

#RUN FASTQC RAWDATA=========================================================================================
echo "Starting FastQC with ${Threads} threads"
for id in `cat /home/Pipeline/sampleList.txt`; do
#CREATE OUTPUTFOLDER IF NOT EXISTS--------------------------------------------------------------------------
     mkdir -p /home/Pipeline/Hybrid/${id}/Short_reads/01_QC-Rawdata/QC_FastQC
#RUN FASTQC-------------------------------------------------------------------------------------------------
     for i in $(ls /home/Pipeline/Hybrid/${id}/Short_reads/00_Rawdata | grep fastq.gz); do
          echo -e "STARTING ${i} \n";
          fastqc --extract \
          -t ${Threads} \
          -o /home/Pipeline/Hybrid/${id}/Short_reads//01_QC-Rawdata/QC_FastQC \
          /home/Pipeline/Hybrid/${id}/Short_reads/00_Rawdata/${i} \
          2>&1 | tee -a /home/Pipeline/Hybrid/${id}/Short_reads/01_QC-Rawdata/QC_FastQC/stdout_err.txt ;
          echo -e "\n ${i} FINISHED \n";
     done
done
#==============================================================================================================

