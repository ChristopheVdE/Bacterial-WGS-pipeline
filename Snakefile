############################################################################################################
#NAME:  SNAKEMAKE
#AUTHOR: Christophe Van den Eynde
#RUNNING: Salmonella t. pipeline for Illumina reads
#USAGE: $snakemake
############################################################################################################

#SNAKEMAKE RUN PREPARATION==================================================================================
# TIMER-----------------------------------------------------------------------------------------------------
import time
start = time.time()
#-----------------------------------------------------------------------------------------------------------

# GET LOCATIONS---------------------------------------------------------------------------------------------
# get current directory
location = os.getcwd()
print("location={}".format(location))

# get other locations
env = open(location+"/enviroment.txt","r")
for line in env.readlines():
    if "location_m=" in line:
        location_m = line.replace("location_m=",'').replace('\n','')
        print(location_m)
    elif "location=" in line:
        location = line.replace("location=",'').replace('\n','')
        print(location)
    elif "origin_m=" in line:
        origin_m = line.replace("origin_m=",'').replace('\n','')
        print(origin_m)
    elif "origin=" in line:
        origin = line.replace("origin=",'').replace('\n','')
        print(origin)
env.close()
#-----------------------------------------------------------------------------------------------------------

#GET SAMPLE IDS---------------------------------------------------------------------------------------------
ids = []
samples = open(location+"/data/sampleList.txt","r")
for line in samples.readlines():
    ids.append(line.replace('\n',''))
samples.close()
#-----------------------------------------------------------------------------------------------------------
#===========================================================================================================

#SNAKEMAKE RUN==============================================================================================
#-----------------------------------------------------------------------------------------------------------
# Master rule, controls all other rule executions

rule all:                                                                       
    input:
        expand(location+"/data/{id}/01_QC-Rawdata/QC_MultiQC/multiqc_report.html",id=ids),                            
        expand(location+"/data/{id}/03_QC-Trimmomatic_Paired/QC_MultiQC/multiqc_report.html",id=ids),                       
        expand(location+"/data/{id}/04_SPAdes/dataset.info",id=ids)                                             
    message:
        "Analysis done, results can be found in {location}/data"

#-----------------------------------------------------------------------------------------------------------
# Pipeline step1: copying files from original raw data folder to data-folder of current analysis

rule copy_rawdata:
    input: 
        expand(origin+"/{id}_L001_R1_001.fastq.gz",id=ids),
        expand(origin+"/{id}_L001_R2_001.fastq.gz",id=ids)
    output:
        expand(location+"/data/{id}/00_Rawdata/{id}_L001_R1_001.fastq.gz",id=ids),
        expand(location+"/data/{id}/00_Rawdata/{id}_L001_R2_001.fastq.gz",id=ids)
    message:
        "Please wait while the rawdata is being copied to the current-analysis folder"
    shell:
        "docker run -it --rm --name copy_rawdata -v /var/run/docker.sock:/var/run/docker.sock -v {origin_m}:/home/rawdata/ -v {location_m}:/home/Pipeline/ christophevde/ubuntu_bash:test /home/Scripts/01_copy_rawdata.sh"
    
#-----------------------------------------------------------------------------------------------------------
# Pipeline step2: running fastqc on the raw-data in the current-analysis folder

rule fastqc_raw:
    input:
        expand(location+"/data/{id}/00_Rawdata/{id}_L001_R1_001.fastq.gz",id=ids),   #the rawdata (output copy_rawdata rule)
        expand(location+"/data/{id}/00_Rawdata/{id}_L001_R2_001.fastq.gz",id=ids)   #the rawdata (output copy_rawdata rule)
    output:
        expand(location+"/data/{id}/01_QC-Rawdata/QC_FastQC/{id}_L001_R1_001_fastqc.html",id=ids),
        expand(location+"/data/{id}/01_QC-Rawdata/QC_FastQC/{id}_L001_R2_001_fastqc.html",id=ids)
    message:
        "Analyzing raw-data with FastQC using Docker-container fastqc:test"
    shell:
        "docker run -it --rm --name fastqc_raw -v /var/run/docker.sock:/var/run/docker.sock -v {location_m}/data:/home/data/ christophevde/fastqc:test /home/Scripts/QC01_fastqcRawData.sh"

#-----------------------------------------------------------------------------------------------------------
# Pipeline step3: running multiqc on the raw-data in the current-analysis folder

rule multiqc_raw:
    input:
        expand(location+"/data/{id}/01_QC-Rawdata/QC_FastQC/{id}_L001_R1_001_fastqc.html",id=ids),    #output fastqc rawdata
        expand(location+"/data/{id}/01_QC-Rawdata/QC_FastQC/{id}_L001_R2_001_fastqc.html",id=ids)     #output fastqc rawdata
    output:
        expand(location+"/data/{id}/01_QC-Rawdata/QC_MultiQC/multiqc_report.html",id=ids)             #Results MultiQC for each sample separately
    message:
        "Analyzing raw-data with MultiQC using Docker-container multiqc:test"
    shell:
        "docker run -it --rm --name multiqc_raw -v /var/run/docker.sock:/var/run/docker.sock -v {location_m}/data:/home/data/ christophevde/multiqc:test /home/Scripts/QC01_multiqc_raw.sh"

#-----------------------------------------------------------------------------------------------------------
# Pipeline step4: Trimming

rule Trimming:
    input:
        expand(location+"/data/{id}/00_Rawdata/{id}_L001_R1_001.fastq.gz",id=ids),          #the rawdata (output copy_rawdata rule)
        expand(location+"/data/{id}/00_Rawdata/{id}_L001_R2_001.fastq.gz",id=ids),          #the rawdata (output copy_rawdata rule)
        expand(location+"/data/{id}/01_QC-Rawdata/QC_MultiQC/multiqc_report.html",id=ids)   #output multiqc raw (required so that the tasks don't run simultaniously and their outpur gets mixed in the terminal)
    output:
        expand(location+"/data/{id}/02_Trimmomatic/{id}_L001_R1_001_P.fastq.gz",id=ids),
        expand(location+"/data/{id}/02_Trimmomatic/{id}_L001_R2_001_U.fastq.gz",id=ids)
    message:
        "Trimming raw-data with Trimmomatic v0.39 using Docker-container trimmomatic:test"
    shell:
        "docker run -it --rm --name trimmomatic -v /var/run/docker.sock:/var/run/docker.sock -v {location_m}/data:/home/data/ christophevde/trimmomatic:test /home/Scripts/02_runTrimmomatic.sh"

#-----------------------------------------------------------------------------------------------------------
# Pipeline step5: FastQC trimmed data (paired reads only)

rule fastqc_trimmed:
    input:
        expand(location+"/data/{id}/02_Trimmomatic/{id}_L001_R1_001_P.fastq.gz",id=ids), #output trimmomatic
        expand(location+"/data/{id}/02_Trimmomatic/{id}_L001_R2_001_U.fastq.gz",id=ids)  #output trimmomatic
    output:
        expand(location+"/data/{id}/03_QC-Trimmomatic_Paired/QC_FastQC/{id}_L001_R1_001_P_fastqc.html",id=ids)
    message:
        "Analyzing trimmed-data with FastQC using Docker-container fastqc:test"
    shell:
        "docker run -it --rm --name fastqc_trim -v /var/run/docker.sock:/var/run/docker.sock -v {location_m}/data:/home/data/ christophevde/fastqc:test /home/Scripts/QC02_fastqcTrimmomatic.sh"

#-----------------------------------------------------------------------------------------------------------
# Pipeline step6: MultiQC trimmed data (paired reads only) 

rule multiqc_trimmed:
    input:
        expand(location+"/data/{id}/03_QC-Trimmomatic_Paired/QC_FastQC/{id}_L001_R1_001_P_fastqc.html",id=ids)      #output fastqc trimmed data
    output:
        expand(location+"/data/{id}/03_QC-Trimmomatic_Paired/QC_MultiQC/multiqc_report.html",id=ids)
    message:
        "Analyzing trimmed-data with MultiQC using Docker-container multiqc:test"
    shell:
        "docker run -it --rm --name multiqc_trim -v /var/run/docker.sock:/var/run/docker.sock -v {location_m}/data:/home/data/ christophevde/multiqc:test /home/Scripts/QC02_multiqcTrimmomatic.sh"

#-----------------------------------------------------------------------------------------------------------
# Pipeline step7: SPAdes

rule Spades_InputPathogenwatch:
    input:
        expand(location+"/data/{id}/02_Trimmomatic/{id}_L001_R1_001_P.fastq.gz",id=ids),                # output trimming
        expand(location+"/data/{id}/02_Trimmomatic/{id}_L001_R2_001_U.fastq.gz",id=ids),                # output trimming
        expand(location+"/data/{id}/03_QC-Trimmomatic_Paired/QC_MultiQC/multiqc_report.html",id=ids)    # output multiqc-trimmed
    output:
        expand(location+"/data/{id}/04_SPAdes/dataset.info",id=ids),
        directory(expand(location+"/data/{id}/05_inputPathogenWatch",id=ids))
    message:
        "assembling genome from trimmed-data with SPAdes v3.13.1 using Docker-container SPAdes:test"
    shell:
        "docker run -it --rm --name spades -v /var/run/docker.sock:/var/run/docker.sock -v {location_m}/data:/home/data/ christophevde/spades:test /home/Scripts/03_spades.sh"

#-----------------------------------------------------------------------------------------------------------
#===========================================================================================================

end = time.time()
print(end - start)