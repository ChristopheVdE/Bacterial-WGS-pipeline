#!/bin/bash

###########################################################################################################
#NAME SCRIPT: 01_Unicycler.py
#AUTHOR: Christophe Van den Eynde  
#Hybrid assembly
#USAGE: 'python3 01_Unicycler.py' (Linux) or 'python.exe 01_Unicycler.py' (Windows)
###########################################################################################################

#FUNCTION==================================================================================================
usage() {
	errorcode=" \nERROR -> This script needs 2 parameters:\n
		1: Path to the results folder
		2: barcode of sample
		3: [OPTIONAL] Ammount of threads to use (default = 1)\n"
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 2 ]; then
	usage
fi
echo
#==========================================================================================================

#TAKE INPUT FROM COMMAND LINE==============================================================================
MinIon="${1}/03_Trimming/${2}.fastq.gz"
Results="${1}/04_Assembly/${2}"
start_genes="${1}/start_genes.fasta"
threads=${3:-"1"}
#==========================================================================================================

#RUN UNICYCLER=============================================================================================
# unicycler \-1 short_reads_1.fastq.gz -2 short_reads_2.fastq.gz -l long_reads.fastq.gz -o output_dir
unicycler \
	-l "${MinIon}" \
	-o "${Results}" \
	-t "${threads}" \
	--start_genes "${start_genes}" \
	2>&1 | tee -a "${Results}/${barcode}/stdin_out.txt"
#==========================================================================================================