#!/bin/bash

###########################################################################################################
#NAME SCRIPT: 01_demultiplex.sh
#AUTHOR: Christophe Van den Eynde  
#demuliplex basecalled reads
#USAGE: ./01demultiplex.sh ${input} ${output} ${barcode}
###########################################################################################################

#FUNCTION==================================================================================================
usage() {
	errorcode=" \nERROR -> This script needs 2 parameters:\n
		1: Path to the fastq files you want to demultiplex\n
        2: Location to save the demultiplexing results\n
		3: Run date\n
        4: [OPTIONAL] Ammount of threads to use (default = 1)\n
        5: [OPTIONAL] The Barcoding kit used during the analysis (default = 'EXP-NBD104')\n"; 
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 2 ]; then
	usage
fi
echo
#==========================================================================================================

#VARIABLES=================================================================================================
Input="$1"
Output="$2/Long_reads/$3/01_Demultiplex"
threads=${4:-"1"}
Barcode=${5:-"EXP-NBD104"}
#==========================================================================================================

#DEMULTIPLEXING============================================================================================
# GUPPY ---------------------------------------------------------------------------------------------------
guppy_barcoder \
--input_path "${Input}" \
--save_path "${Output}" \
--barcode_kits ${Barcode} \
-t ${threads} \
#--verbose_logs \
2>&1 | tee -a "${Output}/stdin_out.txt"
#==========================================================================================================
