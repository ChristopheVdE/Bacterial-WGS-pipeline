#!/bin/bash

###################################################################################
#NAME SCRIPT: Snakemake_Linux.sh
#AUTHOR: Christophe Van den Eynde  
#specifies the number of threads to use and executes the snakemake command
#USAGE: ./Snakemake_Linux.sh
###################################################################################

# Starting snakemake
cd "$(dirname "$BASH_SOURCE")"

#ASK INPUT -------------------------------------------------------
echo "ANALYSIS TYPE"
echo  "- For short read assembly, input: '1' or 'short'"
echo  "- For long read assembly, input: '2' or 'long'"
echo  "- For hybrid assembly, input: '3' or 'hybrid'"
read -p "Please provide Analysis type here: " analysis 
echo "\n"
#-----------------------------------------------------------------

# GO TO REAL LOCATION OF SCRIPT (REQUIRED FOR MAC)----------------
cd "$(dirname "$BASH_SOURCE")"

# SHORT READ WRAPPER----------------------------------------------
if ${analysis}==1 or ${analysis}==short
    then
        echo [SHORT] Starting Short reads assembly
        echo.
        python3 short_read_assembly.py
# LONG READ ASSEMBLY-----------------------------------------------
elif ${analysis}==2 or ${analysis}==long;
    then
        echo [LONG] Starting Long reads assembly
        echo.
        python3 long_read_assembly.py
# HYBRID ASSEMBLY---------------------------------------------------
elif ${analysis}==3 or ${analysis}==hybrid
    then
        echo [HYBRID] Starting Hybrid assembly
        echo.
        python3 hybrid_assembly.py
fi
# ------------------------------------------------------------------