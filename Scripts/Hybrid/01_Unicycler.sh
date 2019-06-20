#!/bin/bash

###########################################################################################################
#NAME SCRIPT: 01_Unicycler.sh
#AUTHOR: Christophe Van den Eynde  
#Hybrid assembly
#USAGE:  ./01_Unicycler.sh'
###########################################################################################################

#FUNCTION==================================================================================================
usage() {
	errorcode=" \nERROR -> This script needs 2 parameters:\n
		1: Sample ID (Illumina)
		2: Barcode (MinION)
		3: Path to the results folder
		3: [OPTIONAL] Ammount of threads to use (default = 1)\n"
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 3 ]; then
	usage
fi
echo
#==========================================================================================================

#TAKE INPUT FROM COMMAND LINE==============================================================================
Illumina1="${3}/01_Short_reads/${1}/02_Trimmomatic/${1}_L001_R1_001_P.fastq.gz"
Illumina2="${3}/01_Short_reads/${1}/02_Trimmomatic/${1}_L001_R2_001_P.fastq.gz"
MinIon="${3}/02_Long_reads/03_Trimming/BC${2}.fastq.gz"
Results="${3}/03_Assembly/${1}"
start_genes="${3}/start_genes.fasta"
threads=${3:-"1"}
#==========================================================================================================

#RUN UNICYCLER=============================================================================================
# unicycler \-1 short_reads_1.fastq.gz -2 short_reads_2.fastq.gz -l long_reads.fastq.gz -o output_dir
unicycler \
	-1 "${Illumina1}"
	-2 "${Illumina2}"
	-l "${MinIon}" \
	-o "${Results}" \
	-t "${threads}" \
	--no_correct \
	--start_genes "${start_genes}"
#==========================================================================================================