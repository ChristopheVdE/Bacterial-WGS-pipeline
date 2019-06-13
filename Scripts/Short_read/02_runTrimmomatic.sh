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
	errorcode=" \nERROR -> This script needs 1 parameters:\n
		1: Analysis type\n
        2: [OPTIONAL] Ammount of threads to use (default = 1)\n";
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 1 ]; then
	usage
fi
echo
#-----------------------------------------------------------------------------------------------------------

#VARIABLES--------------------------------------------------------------------------------------------------
Analysis=$1
Threads=${2:-"1"}
#-----------------------------------------------------------------------------------------------------------

#INPUT AND OUTPUT FOLDER------------------------------------------------------------------------------------
if "$Analysis" = "short"; then
	folder="Short_reads"
elif "$Analysis" = "hybrid"; then
	folder="Hybrid/Short_reads"
fi
# inputFolder = /home/Pipeline/${folder}/${id}/00_Rawdata
# outputFolder = /home/Pipeline/${folder}/${id}/02_Trimmomatic
#-----------------------------------------------------------------------------------------------------------

#TRIMMOMATIC PRE-START--------------------------------------------------------------------------------------
ADAPTERFILE='/home/adapters/NexteraPE-PE.fa';
#Fix possible EOL errors in sampleList.txt
dos2unix -q /home/Pipeline/${folder}/sampleList.txt
#-----------------------------------------------------------------------------------------------------------

#RUN TRIMMOMATIC--------------------------------------------------------------------------------------------
echo "Starting Trimmomatic with ${Threads} threads"
for id in `cat /home/Pipeline/${folder}/sampleList.txt`; do
	#SPECIFY VARIABLES
	# inputFolder = /home/Pipeline/${folder}/${id}/00_Rawdata
	# outputFolder = /home/Pipeline/${folder}/${id}/02_Trimmomatic

	#CREATE OUTPUTFOLDER IF NOT EXISTS
	mkdir -p /home/Pipeline/${folder}/${id}/02_Trimmomatic

	#CREATE temp folder-content-list
	ls /home/Pipeline/${folder}/${id}/00_Rawdata > /home/foldercontent.txt
	sed 's/_L001_R1_001.fastq.gz//g' /home/foldercontent.txt > /home/foldercontent2.txt
	sed 's/_L001_R2_001.fastq.gz//g' /home/foldercontent2.txt > /home/foldercontent3.txt
	uniq -d /home/foldercontent3.txt > /home/foldercontent4.txt; 

	#RUN TRIMMOMATIC
	for i in `cat /home/foldercontent4.txt`; do
		echo -e "\nSTARTING ${i} \n";
		java -jar /home/Trimmomatic-0.39/trimmomatic-0.39.jar  \
		PE -threads ${Threads} -phred33 -trimlog /home/Pipeline/${folder}/${i}/02_Trimmomatic/trimlog.txt \
		/home/Pipeline/${folder}/${i}/00_Rawdata/${folder}/${i}_L001_R1_001.fastq.gz /home/Pipeline/${folder}/${i}/00_Rawdata/${folder}/${i}_L001_R2_001.fastq.gz \
		/home/Pipeline/${folder}/${i}/02_Trimmomatic/${folder}/${i}_L001_R1_001_P.fastq.gz /home/Pipeline/${folder}/${i}/02_Trimmomatic/${folder}/${i}_L001_R1_001_U.fastq.gz \
		/home/Pipeline/${folder}/${i}/02_Trimmomatic/${folder}/${i}_L001_R2_001_P.fastq.gz /home/Pipeline/${folder}/${i}/02_Trimmomatic/${folder}/${i}_L001_R2_001_U.fastq.gz \
		ILLUMINACLIP:${ADAPTERFILE}:2:40:15 LEADING:20 TRAILING:20 SLIDINGWINDOW:4:20 MINLEN:36 \
		2>&1 | tee -a /home/Pipeline/${i}/02_Trimmomatic/stdout_err.txt;
	done
done
#-----------------------------------------------------------------------------------------------------------