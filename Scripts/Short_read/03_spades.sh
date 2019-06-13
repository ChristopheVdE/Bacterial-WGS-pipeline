#!/bin/bash

##########################################################################################################
#NAME SCRIPT: 03_spades.sh
#AUTHOR: Tessa de Block
#DOCKER UPDATE: Christophe Van den Eynde
#ASSEMBLING READS WITH SPADES
#USAGE: ./03_SPADES.SH <number of threads> 
###########################################################################################################

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
#inputSpades=/home/Pipeline/${folder}/${id}/02_Trimmomatic
#outputSpades=/home/Pipeline/${folder}/${id}/04_Spades
#outputPathwatch=/home/Pipeline/${folder}/${id}/05_inputPathogenWatch
#-----------------------------------------------------------------------------------------------------------

#Fix possible EOL errors in sampleList.txt------------------------------------------------------------------
dos2unix -q /home/Pipeline/${folder}/sampleList.txt
#-----------------------------------------------------------------------------------------------------------

#RUNNING SPADES---------------------------------------------------------------------------------------------
echo "Starting SPAdes with ${Threads} threads"
for id in `cat /home/Pipeline/${folder}/sampleList.txt`; do

	#CREATE OUTPUTFOLDERS
	mkdir -p /home/Pipeline/${folder}/${id}/04_SPAdes
	mkdir -p /home/Pipeline/${folder}/${id}/05_inputPathogenWatch

	#CREATE temp folder-content-list
	ls /home/Pipeline/${folder}/${id}/02_Trimmomatic > /home/foldercontent.txt
	sed 's/_L001_R1_001_P.fastq.gz//g' /home/foldercontent.txt > /home/foldercontent2.txt
	sed 's/_L001_R1_001_U.fastq.gz//g' /home/foldercontent2.txt > /home/foldercontent3.txt
	sed 's/_L001_R2_001_P.fastq.gz//g' /home/foldercontent3.txt > /home/foldercontent4.txt
	sed 's/_L001_R1_001_U.fastq.gz//g' /home/foldercontent4.txt > /home/foldercontent5.txt
	uniq -d /home/foldercontent5.txt > /home/foldercontent6.txt; 

	#RUN SPADES AND RENAME
	for i in `cat /home/foldercontent6.txt`; do
		#START SPADES
		echo -e "\nSTARTING ${i} \n";	
		/SPAdes-3.13.1-Linux/bin/spades.py --pe1-1 /home/Pipeline/${folder}/${id}/02_Trimmomatic/${id}_L001_R1_001_P.fastq.gz \
		--pe1-2 /home/Pipeline/${folder}/${id}/02_Trimmomatic/${id}_L001_R2_001_P.fastq.gz \
		--tmp-dir /home/SPAdes/temp/ \
		-o /home/Pipeline/${folder}/${id}/04_SPAdes -t ${Threads};
		#RENAME AND MOVE RESULTS
		cd /home/Pipeline/${folder}/${id}/04_SPAdes
		cp contigs.fasta /home/Pipeline/${folder}/${id}/05_inputPathogenWatch/${id}.fasta
	done
done

	