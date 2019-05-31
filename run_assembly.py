############################################################################################################
#NAME: run_assembly.py
#AUTHOR: Christophe Van den Eynde
#FUNCTION: creates some texts files containing location variables that are used by the snakefile as input
#USAGE: pyhton3 get_enviroment.py
############################################################################################################

#TIMER START================================================================================================
import datetime
start = datetime.datetime.now()
#===========================================================================================================

#IMPORT PACKAGES============================================================================================
import os
#===========================================================================================================

#FUNCTIONS==================================================================================================
#INPUT------------------------------------------------------------------------------------------------------
#PATH CORRECTION--------------------------------------------------------------------------------------------

#SAVING INPUT TO FILE---------------------------------------------------------------------------------------

#SHORT READ SAMPLE LIST CREATION----------------------------------------------------------------------------
def sample_list(Illumina):
    ids =[]
    for sample in os.listdir(Illumina):
        if ".fastq.gz" in sample:
            ids.append(sample.replace('_L001_R1_001.fastq.gz','').replace('_L001_R2_001.fastq.gz',''))
    ids = sorted(set(ids))
    return ids
#===========================================================================================================

#ANALYSIS TYPE==============================================================================================
analysis = input("\nInput analysis type here: \
    \n  - For short read assembly, input: '1' or 'short' \
    \n  - For long read assembly, input: '2' or 'long' \
    \n  - For hybrid assembly, input: '3' or 'hybrid'\n")
#===========================================================================================================

#SHORT READ ONLY ASSEMBLY===================================================================================
if analysis == "1" or analysis == "short":
#GET INPUT--------------------------------------------------------------------------------------------------
    print("\nShort read assembly selected.")
    Illumina = input("Input location of Illumina sample files here: \n")
    Results = input("Input location to store the results here : \n")
#CREATE REQUIRED FOLDERS IF NOT EXIST-----------------------------------------------------------------------
#CONVERT MOUNT_PATHS (INPUT) IF REQUIRED--------------------------------------------------------------------
#SAVE INPUT TO FILE-----------------------------------------------------------------------------------------
#CREATE ILLUMINA SAMPLE LIST + WRITE TO FILE----------------------------------------------------------------
#COPY ILLUMINA SAMPLES TO RESULTS---------------------------------------------------------------------------
#SHORT READS: RUN PIPELINE----------------------------------------------------------------------------------
#===========================================================================================================

#LONG READ ONLY ASSEMBLY====================================================================================
elif analysis == "2" or analysis == "long":
#GET INPUT--------------------------------------------------------------------------------------------------
    print("\nLong read assembly selected.")
    MinIon = input("Input location of MinIon sample files here: \n")
    Results = input("Input location to store the results here : \n")
#CREATE REQUIRED FOLDERS IF NOT EXIST-----------------------------------------------------------------------
#CONVERT MOUNT_PATHS (INPUT) IF REQUIRED--------------------------------------------------------------------
#SAVE INPUT TO FILE-----------------------------------------------------------------------------------------
#CREATE MINION SAMPLE LIST + WRITE TO FILE------------------------------------------------------------------
#COPY MINION SAMPLES TO RESULTS-----------------------------------------------------------------------------
#SHORT READS: RUN PIPELINE----------------------------------------------------------------------------------
#===========================================================================================================

#HYBRID ASSEMBLY============================================================================================
elif analysis == "3" or analysis == "hybrid":
#GET INPUT--------------------------------------------------------------------------------------------------
    print("Hybrid assembly selected.")
    MinIon = input("\nInput location of MinIon sample files here: \n")
    Illumina = input("\nInput location of Illumina sample files here: \n")
    Results = input("\nInput location to store the results here \n")
    threads = input("\nInput number of threads here: \n")
#CREATE REQUIRED FOLDERS IF NOT EXIST-----------------------------------------------------------------------
    folders = [Results+"/Short_reads", Results+"/Long_reads"]
    for i in folders:
        if not os.path.exists(i):
            os.mkdir(i)
#CONVERT MOUNT_PATHS (INPUT) IF REQUIRED--------------------------------------------------------------------
    MinIon_m = MinIon
    Illumina_m = Illumina
    Results_m = Results
    print(" - MinIon data={}".format(MinIon_m))
    print(" - Illumina data={}".format(Illumina_m))
    print(" - Results location={}".format(Results_m))
#SAVE INPUT TO FILE-----------------------------------------------------------------------------------------
    loc = open(Results+"/Short_reads/environment.txt", mode="w")
    loc.write("MinIon="+MinIon+"\n")
    loc.write("MinIon_m="+MinIon_m+"\n")
    loc.write("Illumina="+Illumina+"\n")
    loc.write("Illumina_m="+Illumina_m+"\n")
    loc.write("Results="+Results+"\n")
    loc.write("Results_m="+Results_m+"\n")    
    loc.write("threads="+str(threads))
    loc.close()
#CREATE ILLUMINA SAMPLE LIST + WRITE TO FILE----------------------------------------------------------------
    file = open(Results+"/Short_reads/sampleList.txt",mode="w")
    for i in sample_list(Illumina):
        file.write(i+"\n")
    file.close()
#COPY ILLUMINA SAMPLES TO RESULTS---------------------------------------------------------------------------
    copy = 'docker run -it --rm \
        --name copy_rawdata \
        -v "'+Illumina_m+':/home/rawdata/" \
        -v "'+Results_m+'/Short_reads:/home/Pipeline/" \
        christophevde/ubuntu_bash:v2.2_stable \
        /home/Scripts/01_copy_rawdata.sh'
    os.system(copy)
#SHORT READS: TRIMMING & QC---------------------------------------------------------------------------------
    pwd = location = os.getcwd()
    short_read = 'docker run -it --rm \
        --name snakemake \
        --cpuset-cpus="0" \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "'+pwd+'/Snakefiles/:/home/Snakefiles:ro" \
        -v "'+Results_m+'/Short_reads:/home/Pipeline/" \
        christophevde/snakemake:v2.3_stable \
        /bin/bash -c "cd /home/Snakefiles/Illumina && snakemake; /home/Scripts/copy_log.sh"'
    os.system(short_read)
#LONG READS: DEMULTIPLEXING + TRIMMING----------------------------------------------------------------------
    os.system('sh ./Scripts/Long_read/01_demultiplex.sh '+MinIon+' '+Results+'/Long_reads '+threads)
#===========================================================================================================

#WRONG ASSEMBLY TYPE ERROR==================================================================================
else:
    print("[ERROR] Unknown analysis type")
#===========================================================================================================

#TIMER END==================================================================================================
end = datetime.datetime.now()
timer = end - start
#CONVERT TO HUMAN READABLE----------------------------------------------------------------------------------
print("Analysis took: {} (H:MM:SS) \n".format(timer))
#===========================================================================================================
