#!/bin/bash

############################################################################################################
#NAME SCRIPT: copy_log.sh
#AUTHOR: Christophe Van den Eynde  
#copying the snakemake log to a shared folder
#USAGE: ./copy_log.sh ${input} ${output}
############################################################################################################

#FUNCTION--------------------------------------------------------------------------------------------------
usage() {
	errorcode=" \nERROR -> This script can have only 1 parameter:\n
          1: [OPTIONAL] Run date\n";
	echo ${errorcode};
	exit 1;
}
if [ "$#" -gt 1 ]; then
	usage
fi
echo
#-----------------------------------------------------------------------------------------------------------

#VARIABLES--------------------------------------------------------------------------------------------------
Run="$1"
#----------------------------------------------------------------------------------------------------------

# COPY SNAKEMAKE LOG----------------------------------------------------------------------------------------
echo -e "\nCopying snakemake log, please wait"
mkdir -p /home/Pipeline/Hybrid/${Run}/01_Short_reads/Snakemake_logs/
mv -vu /home/Scripts/Hybrid/Short_read/.snakemake/log/* /home/Pipeline/Hybrid/${Run}/01_Short_reads/Snakemake_logs/
echo -e "Done\n"
#-----------------------------------------------------------------------------------------------------------