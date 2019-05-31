#!/bin/bash

###################################################################################
#NAME SCRIPT: 01_demultiplex.sh
#AUTHOR: Christophe Van den Eynde  
#demuliplex basecalled reads
#USAGE: ./01demultiplex.sh ${input} ${output} ${barcode}
###################################################################################

#FUNCTION==========================================================================
usage() {
	errorcode=" \nERROR -> This script needs 2 parameters:\n
		1: Path to the fastq files you want to demultiplex\n
        2: Location to save the demultiplexing results\n
        3: [OPTIONAL] Ammount of threads to use (default = 1)\n
        4: [OPTIONAL] The Barcoding kit used during the analysis (default = 'EXP-NBD104')\n"; 
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 2 ]; then
	usage
fi
echo
#==================================================================================

#VARIABLES=========================================================================
Input=$1
Output="$2/Long_reads/01_demultiplex"
threads=${3:-"1"}
Barcode=${4:-"EXP-NBD104"}
#==================================================================================

#DEMULTIPLEXING====================================================================
# GUPPY -------------------------------------------------------------------------
guppy_barcoder \
--input_path ${Input} \
--save_path "${Output}/01_guppy" \
--barcode_kits ${Barcode} \
-t ${threads} \
#--verbose_logs \
2>&1 | tee -a "${Output}/01_guppy/stdin_out.txt"

# PORECHOP ON GUPPY----------------------------------------------------------------
# run porechop on the reads, correcting demultiplexing done by guppy if required
# porechop will demulitplex and trim reads at the same time 
# disable auto-trimming: add --untrimmed

mkdir "${Output}/02_guppy+porechop/"

porechop \
-i "${Output}/01_guppy" \
-b "${Output}/02_guppy+porechop" \
--verbosity 1 \
--threads ${threads} \
--format fastq.gz \
#--untrimmed \
2>&1 | tee -a "${Output}/02_guppy+porechop/stdin_out.txt"

#==================================================================================

# compare results/ overview of results=============================================
python3 ./02_demultiplex_compare.py ${Output}
#==================================================================================
