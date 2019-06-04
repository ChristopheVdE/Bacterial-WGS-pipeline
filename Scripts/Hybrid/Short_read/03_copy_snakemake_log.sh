#!/bin/bash

############################################################################################################
#NAME SCRIPT: copy_log.sh
#AUTHOR: Christophe Van den Eynde  
#copying the snakemake log to a shared folder
#USAGE: ./copy_log.sh ${input} ${output}
############################################################################################################

# SPECIFY VARIABLES-----------------------------------------------------------------------------------------
run="RUN_"`date +%Y%m%d`
#-----------------------------------------------------------------------------------------------------------

# COPY SNAKEMAKE LOG----------------------------------------------------------------------------------------
echo -e "\nCopying snakemake log, please wait"
mkdir -p /home/Pipeline/Hybrid/Short_reads/Snakemake_logs/
cp -vr /home/Scripts/Hybrid/Short_read/.snakemake/log/* /home/Pipeline/Hybrid/Short_reads/Snakemake_logs/ 
echo -e "Done\n"
#-----------------------------------------------------------------------------------------------------------