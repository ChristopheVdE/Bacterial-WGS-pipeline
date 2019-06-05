#!/bin/bash

###########################################################################################################
#NAME SCRIPT: 03_Trimming.sh
#AUTHOR: Christophe Van den Eynde  
#demuliplex basecalled reads
#USAGE: ./03_Trimming.sh ${input} ${output} ${barcode}
###########################################################################################################

#FUNCTION==================================================================================================
usage() {
	errorcode=" \nERROR -> This script needs 2 parameters:\n
		1: Path to the fastq files you want to demultiplex\n
        2: Location to save the demultiplexing results\n
		3: [OPTIONAL] Run date\n
        4: [OPTIONAL] Ammount of threads to use (default = 1)\n"
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 2 ]; then
	usage
fi
echo
#==========================================================================================================

#VARIABLES=================================================================================================
Input=$1
Output="$2/Hybrid/$3/02_Long_reads/03_Trimming"
threads=${4:-"1"}
#==========================================================================================================

#DEMULTIPLEXING + TRIMMING=================================================================================
# PORECHOP ON GUPPY----------------------------------------------------------------------------------------
# run porechop on the reads, correcting demultiplexing done by guppy if required
# porechop will demulitplex and trim reads at the same time 
# disable auto-trimming: add --untrimmed

mkdir -p "${Output}"

porechop \
-i "${Input}" \
-b "${Output}" \
--verbosity 1 \
--threads ${threads} \
--format fastq.gz \
#--untrimmed \
2>&1 | tee -a "${Output}/stdin_out.txt"

#==========================================================================================================

# compare results/ overview of results=====================================================================
python3 ./04_demultiplex_compare.py ${Input} ${Output}
#==========================================================================================================