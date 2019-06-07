#!/bin/bash

###########################################################################################################
#NAME SCRIPT: 02_pycoQC.sh
#AUTHOR: Christophe Van den Eynde  
#Intermediate QC for nanopore reads
#USAGE: ./02_pycoQC.sh {fast5} {results} {threads}
###########################################################################################################

#FUNCTION==================================================================================================
usage() {
	errorcode=" \nERROR -> This script needs 2 parameters:\n
		1: Path to the fast5 files\n
        2: Location to save the results\n
        3: [OPTIONAL] Ammount of threads to use (default = 1)\n";
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 3 ]; then
	usage
fi
echo
#==========================================================================================================

#Variables-------------------------------------------------------------------------------------------------
fast5=$1
results=$2
Threads=$3
#----------------------------------------------------------------------------------------------------------

#Create sequencing_summary.txt-----------------------------------------------------------------------------
Fast5_to_seq_summary \
    --fast5_dir ${fast5} \
    --seq_summary_fn ${results}/sequencing_summary.txt \
    -t ${Threads} \
    2>&1 | tee -a ${results}/02_Long_reads/02_QC/fast5-to-fastq_stdin_out.txt
#----------------------------------------------------------------------------------------------------------

#PREFORM PYCOQC--------------------------------------------------------------------------------------------
pycoQC \
    --summary_file ${results}/sequencing_summary.txt \
    --barcode_file ${results}/02_Long_reads/01_Demultiplex/barcoding_summary.txt \
    --html_outputfile ${resutls}/02_Long_reads/02_QC/QC_Long_reads.html \
    --json_outputfile ${resutls}/02_Long_reads/02_QC/QC_Long_reads.json \
    2>&1 |tee -a ${results}/02_Long_reads/02_QC/pycoQC_stdin_out.txt
#----------------------------------------------------------------------------------------------------------
