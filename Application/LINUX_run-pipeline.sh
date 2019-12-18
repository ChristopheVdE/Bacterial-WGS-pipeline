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
echo $analysis
#-----------------------------------------------------------------

# GO TO REAL LOCATION OF SCRIPT (REQUIRED FOR MAC)----------------
cd "$(dirname "$BASH_SOURCE")"

# SHORT READ WRAPPER----------------------------------------------
if [ ${analysis} == 1 ]; then
    echo "[SHORT] Starting Short reads assembly"
    python3 ./Scripts/Short_read/short_read_assembly.py
elif [ ${analysis} == 'short' ]; then
    echo "[SHORT] Starting Short reads assembly"
    python3 ./Scripts/Short_read/short_read_assembly.py
# LONG READ ASSEMBLY-----------------------------------------------
elif [ ${analysis} == 2 ]; then
    echo "[LONG] Starting Long reads assembly"
    python3 ./Scripts/Long_read/long_read_assembly.py
elif [ ${analysis} == 'long' ]; then
    echo "[LONG] Starting Long reads assembly"
    python3 ./Scripts/Long_read/long_read_assembly.py
# HYBRID ASSEMBLY---------------------------------------------------
elif [ ${analysis} == 3 ]; then
    echo "[HYBRID] Starting Hybrid assembly"
    python3 ./Scripts/Hybrid/hybrid_assembly.py
elif [ ${analysis} == 'hybrid' ]; then
    echo "[HYBRID] Starting Hybrid assembly"
    python3 ./Scripts/Hybrid/hybrid_assembly.py
fi
# ------------------------------------------------------------------