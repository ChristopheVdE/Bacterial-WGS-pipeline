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
	errorcode=" \nERROR -> This script can have only 3 parameters:\n
          1: Sample ID
          2: [OPTIONAL] Run date\n
          3: [OPTIONAL] Ammount of threads to use (default = 1)\n";
	echo ${errorcode};
	exit 1;
}
if [ "$#" -gt 3 ]; then
	usage
fi
echo
#-----------------------------------------------------------------------------------------------------------

#VARIABLES--------------------------------------------------------------------------------------------------
Sample="$1"
Run="$2"
Threads=${3:-"1"}
#-----------------------------------------------------------------------------------------------------------

#CREATE OUTPUTFOLDER IF NOT EXISTS--------------------------------------------------------------------------
mkdir -p /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/03_QC-Trimmomatic_Paired/QC_FastQC
#-----------------------------------------------------------------------------------------------------------

#RUN FASTQC TRIMMED DATA====================================================================================
echo "Starting FastQC with ${Threads} threads"
for i in $(ls /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/02_Trimmomatic | grep _P.fastq.gz); do
    echo -e "STARTING FastQC on paired reads of ${i} \n";
    fastqc --extract \
    -t ${Threads} \
    -o /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/03_QC-Trimmomatic_Paired/QC_FastQC \
    /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/02_Trimmomatic/${i} \
    2>&1 | tee -a /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/03_QC-Trimmomatic_Paired/QC_FastQC/stdout_err.txt ;
    echo -e "\n ${i} FINISHED \n";
done
#============================================================================================================