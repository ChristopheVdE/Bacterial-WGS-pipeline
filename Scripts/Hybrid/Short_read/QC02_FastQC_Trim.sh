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
          1: [OPTIONAL] Run date\n
          2: [OPTIONAL] Ammount of threads to use (default = 1)\n";
	echo ${errorcode};
	exit 1;
}
if [ "$#" -gt 2 ]; then
	usage
fi
echo
#-----------------------------------------------------------------------------------------------------------

#VARIABLES--------------------------------------------------------------------------------------------------
Run="$1"
Threads=${2:-"1"}
#-----------------------------------------------------------------------------------------------------------

#FASTQC PRE-START-------------------------------------------------------------------------------------------
#Fix possible EOL errors in sampleList.txt
dos2unix -q /home/Pipeline/Hybrid/${Run}/sampleList.txt
echo
#-----------------------------------------------------------------------------------------------------------

#RUN FASTQC TRIMMED DATA====================================================================================
echo "Starting FastQC with ${Threads} threads"
for id in `cat /home/Pipeline/Hybrid/${Run}/sampleList.txt`; do
#CREATE OUTPUTFOLDER IF NOT EXISTS--------------------------------------------------------------------------
    mkdir -p /home/Pipeline/Hybrid/${Run}/01_Short_reads/${id}/03_QC-Trimmomatic_Paired/QC_FastQC
#RUN FASTQC-------------------------------------------------------------------------------------------------
    for i in $(ls /home/Pipeline/Hybrid/${Run}/01_Short_reads/${id}/02_Trimmomatic | grep _P.fastq.gz); do
        echo -e "STARTING FastQC on paired reads of ${i} \n";
        fastqc --extract \
        -t ${Threads} \
        -o /home/Pipeline/Hybrid/${Run}/01_Short_reads/${id}/03_QC-Trimmomatic_Paired/QC_FastQC \
        /home/Pipeline/Hybrid/${Run}/01_Short_reads/${id}/02_Trimmomatic/${i} \
        2>&1 | tee -a /home/Pipeline/Hybrid/${Run}/01_Short_reads/${id}/03_QC-Trimmomatic_Paired/QC_FastQC/stdout_err.txt ;
        echo -e "\n ${i} FINISHED \n";
    done
done
#============================================================================================================