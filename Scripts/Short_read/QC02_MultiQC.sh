#!bin/bash

############################################################################################################
#NAME SCRIPT: MultiQC.sh
#AUTHOR: Christophe van den Eynde
#RUNNING MultiQC
#USAGE: ./runMultiQC.sh
############################################################################################################

#FUNCTION--------------------------------------------------------------------------------------------------
usage() {
	errorcode=" \nERROR -> This script needs 2 parameters:\n
          1: Analysis type\n
          2: Analysis step ('raw' or 'trimmed') \n";
	echo ${errorcode};
	exit 1;
}
if [ "$#" -lt 2 ]; then
	usage
fi
echo
#-----------------------------------------------------------------------------------------------------------

#VARIABLES--------------------------------------------------------------------------------------------------
Analysis=$1
Step=$2
#-----------------------------------------------------------------------------------------------------------

#INPUT AND OUTPUT FOLDER------------------------------------------------------------------------------------
if "$Analysis" = "short"; then
	folder="Short_reads"
elif "$Analysis" = "hybrid"; then
	folder="Hybrid/Short_reads"
fi
#-----------------------------------------------------------------------------------------------------------

#MultiQC PRE-START------------------------------------------------------------------------------------------
#Fix possible EOL errors in sampleList.txt
dos2unix /home/Pipeline/${folder}/sampleList.txt
#-----------------------------------------------------------------------------------------------------------

if ${Step} == "raw"; then
      #===========================================================================================================
      # 1) MULTIQC FULL RUN (RAWDATA)
      #===========================================================================================================

      # CREATE FOLDERS--------------------------------------------------------------------------------------------
      # create temp folder in container (will automatically be deleted when container closes)
      mkdir -p /home/fastqc-results
      # create outputfolder MultiQC full run Rawdata
      run="RUN_"`date +%Y%m%d`
      mkdir -p /home/Pipeline/${folder}/QC_MultiQC/${run}/QC-Rawdata
      #-----------------------------------------------------------------------------------------------------------

      # COLLECT FASTQC DATA---------------------------------------------------------------------------------------
      # collect all fastqc results of the samples in this run into this temp folder
      for id in `cat /home/Pipeline/${folder}/sampleList.txt`; do
            cp -r /home/Pipeline/${id}/01_QC-Rawdata/QC_FastQC/* /home/fastqc-results/
      done
      #-----------------------------------------------------------------------------------------------------------

      # MultiQC FULL RUN------------------------------------------------------------------------------------------
      echo -e "\nStarting MultiQC on Full RUN\n"
      echo "----------"
      multiqc /home/fastqc-results/ \
      -o /home/Pipeline/${folder}/QC_MultiQC/${run}/QC-Rawdata \
      2>&1 | tee -a /home/Pipeline/${folder}/QC_MultiQC/${run}/QC-Rawdata/stdout_err.txt;
      echo "----------"
      echo -e "\nDone"
      #-----------------------------------------------------------------------------------------------------------

      #===========================================================================================================
      # 2) MULTIQC ON EACH SAMPLE (SEPARATELY)
      #===========================================================================================================

      #EXECUTE MultiQC--------------------------------------------------------------------------------------------
      for id in `cat /home/Pipeline/${folder}/sampleList.txt`; do
            #CREATE OUTPUTFOLDER IF NOT EXISTS
            cd /home/Pipeline/${folder}/${id}/01_QC-Rawdata/
            mkdir -p QC_MultiQC/
            #RUN MultiQC
            echo -e "\nStarting MultiQC on: /home/Pipeline/${id}/01_QC-Rawdata/QC_FastQC/\n"
            echo "----------"
            multiqc /home/Pipeline/${folder}/${id}/01_QC-Rawdata/QC_FastQC/ \
            -o /home/Pipeline/${folder}/${id}/01_QC-Rawdata/QC_MultiQC \
            2>&1 | tee -a /home/Pipeline/${folder}/${id}/01_QC-Rawdata/QC_MultiQC/stdout_err.txt;
            echo "----------"
            echo -e "\nDone"
      done
      #-----------------------------------------------------------------------------------------------------------

elif ${Step} = "trimmed"; then
      #===========================================================================================================
      # 1) MULTIQC FULL RUN (TRIMMED DATA)
      #===========================================================================================================

      # CREATE FOLDERS--------------------------------------------------------------------------------------------
      # create temp folder in container (will automatically be deleted when container closes)
      mkdir -p /home/fastqc-results
      # create outputfolder MultiQC full run trimmed data
      run="RUN_"`date +%Y%m%d`
      mkdir -p /home/Pipeline/${folder}/QC_MultiQC/${run}/QC-Trimmed
      #-----------------------------------------------------------------------------------------------------------

      # COLLECT FASTQC DATA---------------------------------------------------------------------------------------
      # collect all fastqc results of the samples in this run into this temp folder
      for id in `cat /home/Pipeline/sampleList.txt`; do
            cp -r /home/Pipeline/${folder}/${id}/03_QC-Trimmomatic_Paired/QC_FastQC/* /home/fastqc-results/
      done
      #-----------------------------------------------------------------------------------------------------------

      # MultiQC FULL RUN------------------------------------------------------------------------------------------
      echo -e "\nStarting MultiQC on paired-end trimmed data of FULL RUN\n"
      echo "----------"
      multiqc /home/fastqc-results/ \
      -o /home/Pipeline/${folder}/QC_MultiQC/${run}/QC-Trimmed \
      2>&1 | tee -a /home/Pipeline/${folder}/QC_MultiQC/${run}/QC-Trimmed/stdout_err.txt;
      echo "----------"
      echo -e "\nDone"
      #-----------------------------------------------------------------------------------------------------------

      #===========================================================================================================
      # 2) MULTIQC ON EACH SAMPLE (SEPARATELY) (TRIMMED DATA)
      #===========================================================================================================

      #EXECUTE MultiQC--------------------------------------------------------------------------------------------
      for id in `cat /home/Pipeline/${folder}/sampleList.txt`; do
            #CREATE OUTPUTFOLDER IF NOT EXISTS
            cd /home/Pipeline/${folder}/${id}/03_QC-Trimmomatic_Paired/
            mkdir -p QC_MultiQC/
            #RUN MultiQC
            echo -e "\nStarting MultiQC on: /home/Pipeline/${id}/03_QC-Trimmomatic_Paired/QC_FastQC/\n"
            echo "----------"
            multiqc /home/Pipeline/${folder}/${id}/03_QC-Trimmomatic_Paired/QC_FastQC/ \
            -o /home/Pipeline/${folder}/${id}/03_QC-Trimmomatic_Paired/QC_MultiQC \
            2>&1 | tee -a /home/Pipeline/${folder}/${id}/03_QC-Trimmomatic_Paired/QC_MultiQC/stdout_err.txt;
            echo "----------"
            echo -e "\nDone"
      done
      #-----------------------------------------------------------------------------------------------------------
fi