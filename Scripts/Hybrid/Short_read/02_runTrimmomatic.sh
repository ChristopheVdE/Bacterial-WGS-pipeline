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

#TRIMMOMATIC PRE-START--------------------------------------------------------------------------------------
ADAPTERFILE='/home/adapters/NexteraPE-PE.fa';
#Fix possible EOL errors in sampleList.txt
dos2unix -q /home/Pipeline/Hybrid/sampleList.txt
#-----------------------------------------------------------------------------------------------------------

#RUN TRIMMOMATIC--------------------------------------------------------------------------------------------
echo "Starting Trimmomatic with ${Threads} threads"
for id in `cat /home/Pipeline/Hybrid/${Run}/sampleList.txt`; do
	#SPECIFY VARIABLES
	# inputFolder = /home/Pipeline/Hybrid/${Run}/01_Short_reads//${id}/00_Rawdata
	# outputFolder = /home/Pipeline/Hybrid/${Run}/01_Short_reads/${id}/02_Trimmomatic

	#CREATE OUTPUTFOLDER IF NOT EXISTS
	mkdir -p /home/Pipeline/Hybrid/${Run}/01_Short_reads/${id}/02_Trimmomatic

	#CREATE temp folder-content-list
	ls /home/Pipeline/Hybrid/${Run}/01_Short_reads/${id}/00_Rawdata > /home/foldercontent.txt
	sed 's/_L001_R1_001.fastq.gz//g' /home/foldercontent.txt > /home/foldercontent2.txt
	sed 's/_L001_R2_001.fastq.gz//g' /home/foldercontent2.txt > /home/foldercontent3.txt
	uniq -d /home/foldercontent3.txt > /home/foldercontent4.txt; 

	#RUN TRIMMOMATIC
	for i in `cat /home/foldercontent4.txt`; do
		echo -e "\nSTARTING ${i} \n";
		java -jar /home/Trimmomatic-0.39/trimmomatic-0.39.jar  \
		PE -threads ${Threads} -phred33 -trimlog /home/Pipeline/Hybrid/${Run}/01_Short_reads/${i}/02_Trimmomatic/trimlog.txt \
		/home/Pipeline/Hybrid/${Run}/01_Short_reads/${i}/00_Rawdata/${i}_L001_R1_001.fastq.gz /home/Pipeline/Hybrid/${Run}/01_Short_reads/${i}/00_Rawdata/${i}_L001_R2_001.fastq.gz \
		/home/Pipeline/Hybrid/${Run}/01_Short_reads/${i}/02_Trimmomatic/${i}_L001_R1_001_P.fastq.gz /home/Pipeline/Hybrid/${Run}/01_Short_reads/${i}/02_Trimmomatic/${i}_L001_R1_001_U.fastq.gz \
		/home/Pipeline/Hybrid/${Run}/01_Short_reads/${i}/02_Trimmomatic/${i}_L001_R2_001_P.fastq.gz /home/Pipeline/Hybrid/${Run}/01_Short_reads/${i}/02_Trimmomatic/${i}_L001_R2_001_U.fastq.gz \
		ILLUMINACLIP:${ADAPTERFILE}:2:40:15 LEADING:20 TRAILING:20 SLIDINGWINDOW:4:20 MINLEN:36 \
		2>&1 | tee -a /home/Pipeline/Hybrid/${Run}/01_Short_reads/${i}/02_Trimmomatic/stdout_err.txt;
	done
done
#-----------------------------------------------------------------------------------------------------------