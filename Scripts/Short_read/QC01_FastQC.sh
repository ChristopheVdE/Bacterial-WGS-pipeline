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
	errorcode=" \nERROR -> This script needs 2 parameters:\n
          1: Analysis type\n
          2: Analysis step ('raw' or 'trimmed') \n
          3: [OPTIONAL] Ammount of threads to use (default = 1)\n";
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 2 ]; then
	usage
fi
echo
#-----------------------------------------------------------------------------------------------------------

#VARIABLES--------------------------------------------------------------------------------------------------
Analysis=$1
Step=$2
Threads=${2:-"1"}
#-----------------------------------------------------------------------------------------------------------

#INPUT AND OUTPUT FOLDER------------------------------------------------------------------------------------
if Analysis == "short"; then
	folder = "/Short_reads"
elif Analysis == "hybrid"; then
	folder = "/Hybrid/Short_reads"
fi
#-----------------------------------------------------------------------------------------------------------

#FASTQC PRE-START-------------------------------------------------------------------------------------------
#Fix possible EOL errors in sampleList.txt
dos2unix /home/Pipeline/${folder}/sampleList.txt
echo
#-----------------------------------------------------------------------------------------------------------

#RUN FASTQC=================================================================================================
echo "Starting FastQC with ${Threads} threads"
for id in `cat /home/Pipeline/${folder}/sampleList.txt`; do
#RAWDATA----------------------------------------------------------------------------------------------------
     if ${Step} == "raw"; then
     #CREATE OUTPUTFOLDER IF NOT EXISTS
          mkdir -p /home/Pipeline/${folder}/${id}/01_QC-Rawdata/QC_FastQC
          #RUN FASTQC
          for i in $(ls /home/Pipeline/${folder}/${id}/00_Rawdata | grep fastq.gz); do
               echo -e "STARTING ${i} \n";
               fastqc --extract \
               -t ${Threads} \
               -o /home/Pipeline/${folder}/${id}/01_QC-Rawdata/QC_FastQC \
               /home/Pipeline/${folder}/${id}/00_Rawdata/${i} \
               2>&1 | tee -a /home/Pipeline/${folder}/${id}/01_QC-Rawdata/QC_FastQC/stdout_err.txt ;
               echo -e "\n ${i} FINISHED \n";
          done
#TRIMMED DATA-----------------------------------------------------------------------------------------------
     elif ${Step} = "trimmed"; then
          #CREATE OUTPUTFOLDER IF NOT EXISTS
          mkdir -p /home/Pipeline/${folder}/${id}/03_QC-Trimmomatic_Paired/QC_FastQC
          #RUN FASTQC
          for i in $(ls /home/Pipeline/${folder}/${id}/02_Trimmomatic | grep _P.fastq.gz); do
               echo -e "STARTING FastQC on paired reads of ${i} \n";
               fastqc --extract \
               -t ${Threads} \
               -o /home/Pipeline/${folder}/${id}/03_QC-Trimmomatic_Paired/QC_FastQC \
               /home/Pipeline/${folder}/${id}/02_Trimmomatic/${i} \
               2>&1 | tee -a /home/Pipeline/${folder}/${id}/03_QC-Trimmomatic_Paired/QC_FastQC/stdout_err.txt ;
               echo -e "\n ${i} FINISHED \n";
          done
     fi
done
#==============================================================================================================

