#!bin/bash

############################################################################################################
#NAME SCRIPT: QC02_MultiQC_Trimm.sh
#AUTHOR: Christophe van den Eynde
#RUNNING MultiQC
#USAGE: ./QC02_MultiQC_Trim.sh
############################################################################################################

#MultiQC PRE-START------------------------------------------------------------------------------------------
#Fix possible EOL errors in sampleList.txt
dos2unix /home/Pipeline/Hybrid/sampleList.txt
#-----------------------------------------------------------------------------------------------------------

#===========================================================================================================
# 1) MULTIQC FULL RUN (TRIMMED DATA)
#===========================================================================================================

# CREATE FOLDERS--------------------------------------------------------------------------------------------
# create temp folder in container (will automatically be deleted when container closes)
mkdir -p /home/fastqc-results
# create outputfolder MultiQC full run trimmed data
run="RUN_"`date +%Y%m%d`
mkdir -p /home/Pipeline/Hybrid/QC_MultiQC/${run}/QC-Trimmed
#-----------------------------------------------------------------------------------------------------------

# COLLECT FASTQC DATA---------------------------------------------------------------------------------------
# collect all fastqc results of the samples in this run into this temp folder
for id in `cat /home/Pipeline/sampleList.txt`; do
      cp -r /home/Pipeline/Hybrid/${id}/Short_reads/03_QC-Trimmomatic_Paired/QC_FastQC/* /home/fastqc-results/
done
#-----------------------------------------------------------------------------------------------------------

# MultiQC FULL RUN------------------------------------------------------------------------------------------
echo -e "\nStarting MultiQC on paired-end trimmed data of FULL RUN\n"
echo "----------"
multiqc /home/fastqc-results/ \
-o /home/Pipeline/Hybrid/QC_MultiQC/${run}/QC-Trimmed \
2>&1 | tee -a /home/Pipeline/Hybrid/QC_MultiQC/${run}/QC-Trimmed/stdout_err.txt;
echo "----------"
echo -e "\nDone"
#-----------------------------------------------------------------------------------------------------------

#===========================================================================================================
# 2) MULTIQC ON EACH SAMPLE (SEPARATELY) (TRIMMED DATA)
#===========================================================================================================

#EXECUTE MultiQC--------------------------------------------------------------------------------------------
for id in `cat /home/Pipeline/Hybrid/sampleList.txt`; do
      #CREATE OUTPUTFOLDER IF NOT EXISTS
      cd /home/Pipeline/Hybrid/${id}/Short_reads/03_QC-Trimmomatic_Paired/
      mkdir -p QC_MultiQC/
      #RUN MultiQC
      echo -e "\nStarting MultiQC on sample: ${id}\n"
      echo "----------"
      multiqc /home/Pipeline/Hybrid/${id}/Short_reads/03_QC-Trimmomatic_Paired/QC_FastQC/ \
      -o /home/Pipeline/Hybrid/${id}/Short_reads/03_QC-Trimmomatic_Paired/QC_MultiQC \
      2>&1 | tee -a /home/Pipeline/Hybrid/${id}/Short_reads/3_QC-Trimmomatic_Paired/QC_MultiQC/stdout_err.txt;
      echo "----------"
      echo -e "\nDone"
done
#-----------------------------------------------------------------------------------------------------------