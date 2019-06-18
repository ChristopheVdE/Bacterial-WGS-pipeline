#!/bin/bash

############################################################################################################
#NAME SCRIPT: runTrimmomatic.sh
#AUTHOR: Tessa de Block
#DOCKER UPDATE: Christophe Van den Eynde
#RUNNING TRIMMOMATIC
#USAGE: ./runTrimmomatic.sh <number of threads>
############################################################################################################

#FUNCTION--------------------------------------------------------------------------------------------------
usage() {
	errorcode=" \nERROR -> This script can have only 3 parameters:\n
        1: sample id
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
Sample="$3"
Run="$2"
Threads=${3:-"1"}
# inputFolder = /home/Pipeline/Hybrid/${Run}/01_Short_reads/{sample}/00_Rawdata
# outputFolder = /home/Pipeline/Hybrid/${Run}/01_Short_reads/${sample}/02_Trimmomatic
#-----------------------------------------------------------------------------------------------------------

#TRIMMOMATIC PRE-START--------------------------------------------------------------------------------------
ADAPTERFILE='/home/adapters/NexteraPE-PE.fa';
#-----------------------------------------------------------------------------------------------------------

#CREATE OUTPUTFOLDER IF NOT EXISTS--------------------------------------------------------------------------
mkdir -p /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/02_Trimmomatic
#-----------------------------------------------------------------------------------------------------------

#RUN TRIMMOMATIC--------------------------------------------------------------------------------------------
echo "Starting Trimmomatic with ${Threads} threads"
echo -e "\nSTARTING ${Sample} \n";
java -jar /home/Trimmomatic-0.39/trimmomatic-0.39.jar  \
PE -threads ${Threads} -phred33 -trimlog /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/02_Trimmomatic/trimlog.txt \
/home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/00_Rawdata/${Sample}_L001_R1_001.fastq.gz /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/00_Rawdata/${Sample}_L001_R2_001.fastq.gz \
/home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/02_Trimmomatic/${Sample}_L001_R1_001_P.fastq.gz /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/02_Trimmomatic/${Sample}_L001_R1_001_U.fastq.gz \
/home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/02_Trimmomatic/${Sample}_L001_R2_001_P.fastq.gz /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/02_Trimmomatic/${Sample}_L001_R2_001_U.fastq.gz \
ILLUMINACLIP:${ADAPTERFILE}:2:40:15 LEADING:20 TRAILING:20 SLIDINGWINDOW:4:20 MINLEN:36 \
2>&1 | tee -a /home/Pipeline/Hybrid/${Run}/01_Short_reads/${Sample}/02_Trimmomatic/stdout_err.txt;
#-----------------------------------------------------------------------------------------------------------