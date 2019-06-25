#!bin/bash

############################################################################################################
#NAME SCRIPT: multiqcTrimmomatic.sh
#AUTHOR: Christophe van den Eynde
#RUNNING MultiQC
#USAGE: ./runMultiQC.sh
############################################################################################################

#VARIABLES--------------------------------------------------------------------------------------------------
# inputFolder = /home/{id}/03_QC-Trimmomatic_Paired/QC_FastQC
# outputFolder = /home/{id}/03_QC-Trimmomatic_Paired/QC_MultiQC
run=$1
#----------------------------------------------------------------------------------------------------------

#MultiQC PRE-START------------------------------------------------------------------------------------------
#Fix possible EOL errors in sampleList.txt
dos2unix -q /home/Pipeline/sampleList.txt
#-----------------------------------------------------------------------------------------------------------

#===========================================================================================================
# 1) MULTIQC FULL RUN
#===========================================================================================================

# CREATE FOLDERS--------------------------------------------------------------------------------------------
# create temp folder in container (will automatically be deleted when container closes)
mkdir -p /home/fastqc-results
# create outputfolder MultiQC full run trimmed data
mkdir -p /home/Pipeline/QC_MultiQC/${run}/QC-Trimmed
#-----------------------------------------------------------------------------------------------------------

# COLLECT FASTQC DATA---------------------------------------------------------------------------------------
# collect all fastqc results of the samples in this run into this temp folder
for id in `cat /home/Pipeline/sampleList.txt`; do
      cp -r /home/Pipeline/${id}/03_QC-Trimmomatic_Paired/QC_FastQC/* /home/fastqc-results/
done
#-----------------------------------------------------------------------------------------------------------

# MultiQC FULL RUN------------------------------------------------------------------------------------------
echo -e "\nStarting MultiQC on paired-end trimmed data of FULL RUN\n"
echo "----------"
multiqc /home/fastqc-results/ \
-o /home/Pipeline/QC_MultiQC/${run}/QC-Trimmed \
2>&1 | tee -a /home/Pipeline/QC_MultiQC/${run}/QC-Trimmed/stdout_err.txt;
echo "----------"
echo -e "\nDone"
#-----------------------------------------------------------------------------------------------------------

#===========================================================================================================
# 2) MULTIQC ON EACH SAMPLE (SEPARATELY)
#===========================================================================================================

#EXECUTE MultiQC--------------------------------------------------------------------------------------------
for id in `cat /home/Pipeline/sampleList.txt`; do
      #CREATE OUTPUTFOLDER IF NOT EXISTS
      cd /home/Pipeline/${id}/03_QC-Trimmomatic_Paired/
      mkdir -p QC_MultiQC/
      #RUN MultiQC
      echo -e "\nStarting MultiQC on: /home/Pipeline/${id}/03_QC-Trimmomatic_Paired/QC_FastQC/\n"
      echo "----------"
      multiqc /home/Pipeline/${id}/03_QC-Trimmomatic_Paired/QC_FastQC/ \
      -o /home/Pipeline/${id}/03_QC-Trimmomatic_Paired/QC_MultiQC \
      2>&1 | tee -a /home/Pipeline/${id}/03_QC-Trimmomatic_Paired/QC_MultiQC/stdout_err.txt;
      echo "----------"
      echo -e "\nDone"
done
#-----------------------------------------------------------------------------------------------------------

