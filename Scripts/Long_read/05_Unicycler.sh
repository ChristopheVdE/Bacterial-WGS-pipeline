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
		1: Path to the fastq files you want to assemble\n
                2: Location to save the assembly results\n
		3: location of the file containing start genes\n
                4: [OPTIONAL] Ammount of threads to use (default = 1)\n"
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 2 ]; then
	usage
fi
echo
#==========================================================================================================

#TAKE INPUT FROM COMMAND LINE==============================================================================
MinIon="${1}/03_Trimming"
Results="${2}/04_Assembly"
start_genes="${3}/start_genes.fasta"
threads=${4:-"1"}
#==========================================================================================================

#RUN UNICYCLER=============================================================================================
# unicycler \-1 short_reads_1.fastq.gz -2 short_reads_2.fastq.gz -l long_reads.fastq.gz -o output_dir

for i in `ls ${MinIon} | grep "BC"`
    echo "Creating assembly from MinIon sample with Barcode: ${i}"
    unicycler \
        -l "${MinIon}/${i}.fastq.gz "\
        -o "${Results}/${i} "\
        -t "${threads}" \
        --no_correct \
        --start_genes "${start_genes}" \
        2>&1 | tee -a "${Results}/stdin_out.txt"
#==========================================================================================================