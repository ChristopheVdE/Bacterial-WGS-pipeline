#!/bin/bash

###########################################################################################################
#NAME SCRIPT: 02_Prokka.sh
#AUTHOR: Christophe Van den Eynde  
#Hybrid assembly
#USAGE: ./02_Prokka.sh
###########################################################################################################

#FUNCTION==================================================================================================
usage() {
	errorcode=" \nERROR -> This script needs 2 parameters:\n
		1: Path to folder where results should be saved
        2: [OPTIONAL] Genus of organism
        3: [OPTIONAL] Speciesof organism
        4: [OPTIONAL] Kingdom that the organism belongs to
        5: [OPTIONAL] Gram + or - (only for bacteria)
        6: [OPTIONAL] The assembly to annotate
        7: [OPTIONAL] Ammount of threads to use (default = 1)\n"
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 2 ]; then
	usage
fi
echo
#==========================================================================================================

#VARIABLES=================================================================================================
Results=$1
genus=$2
species=$3
kingdom=$4
assembly=$5
threads=${6:-"1"}
#==========================================================================================================

#PROKKA====================================================================================================
prokka \
    --outdir ${Results} \
    --genus ${genus} \
    --species ${species} \
    --kingdom ${kingdom} \
    --cpus ${threads} \
    --force \
    ${assembly}
#==========================================================================================================