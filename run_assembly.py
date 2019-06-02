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
import platform
import subprocess
import string
#===========================================================================================================

#FUNCTIONS==================================================================================================
#INPUT------------------------------------------------------------------------------------------------------
#PATH CORRECTION--------------------------------------------------------------------------------------------
def correct_path(options):
    for key, value in options:
        if sys=="Windows":
            for i in list(string.ascii_lowercase+string.ascii_uppercase):
                if value.startswith(i+":/"):
                    options[key+"_m"] = value.replace(i+":/","/"+i.lower()+"//").replace('\\','/')
                elif value.startswith(i+":\\"):
                    options[key+"_m"] = value.replace(i+":\\","/"+i.lower()+"//").replace('\\','/')
        else:
            options[key+"m"] = options[key]
    return options
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
print("ANALYSIS TYPE"+"="*67)
print(" - For short read assembly, input: '1' or 'short' \
    \n - For long read assembly, input: '2' or 'long' \
    \n - For hybrid assembly, input: '3' or 'hybrid'")
analysis = input("\nInput analysis type here: ")
print("="*80)
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
    print("\nHYBRID ASSEMBLY"+"="*65+"\nOPTIONS"+"-"*73)
    options = {}
    options["MinIon"] = input("Input location of MinIon sample files here: \n")
    options["Illumina"] = input("Input location of Illumina sample files here: \n")
    options["Results"] = input("Input location to store the results here \n")
    options["Threads"] = str(input("Input number of threads here: \n"))
    advanced = input("Go to advanced options? (y/n): ").lower()
    if advanced == "y" or advanced =="yes":
        print("ADVANCED OPTIONS"+"-"*64)
#CREATE REQUIRED FOLDERS IF NOT EXIST-----------------------------------------------------------------------
    folders = [options["Results"]+"/Short_reads", options["Results"]+"/Long_reads"]
    for i in folders:
        if not os.path.exists(i):
            os.mkdir(i)
#CONVERT MOUNT_PATHS (INPUT) IF REQUIRED--------------------------------------------------------------------
    correct_path(options)
    # MinIon_m = MinIon
    # Illumina_m = Illumina
    # Results_m = Results
    # print(" - MinIon data={}".format(MinIon_m))
    # print(" - Illumina data={}".format(Illumina_m))
    # print(" - Results location={}".format(Results_m))
#SAVE INPUT TO FILE-----------------------------------------------------------------------------------------
    loc = open(options["Results"]+"/Short_reads/environment.txt", mode="w")
    for key, value in options.items():
        if not key == "Threads":
            loc.write(key+"="+value+"\n")
        else:
            loc.write(key+"="+value)  
    loc.close()

    # loc = open(Results+"/Short_reads/environment.txt", mode="w")
    # loc.write("MinIon="+MinIon+"\n")
    # loc.write("MinIon_m="+MinIon_m+"\n")
    # loc.write("Illumina="+Illumina+"\n")
    # loc.write("Illumina_m="+Illumina_m+"\n")
    # loc.write("Results="+Results+"\n")
    # loc.write("Results_m="+Results_m+"\n")    
    # loc.write("threads="+Threads)

#CREATE ILLUMINA SAMPLE LIST + WRITE TO FILE----------------------------------------------------------------
    file = open(Results+"/Short_reads/sampleList.txt",mode="w")
    for i in sample_list(Illumina):
        file.write(i+"\n")
    file.close()
#COPY ILLUMINA SAMPLES TO RESULTS---------------------------------------------------------------------------
    copy = 'docker run -it --rm \
        --name copy_rawdata \
        -v "'+options["Illumina_m"]+':/home/rawdata/" \
        -v "'+options["Results_m"]+'/Short_reads:/home/Pipeline/" \
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
        -v "'+options["Results_m"]+'/Short_reads:/home/Pipeline/" \
        christophevde/snakemake:v2.3_stable \
        /bin/bash -c "cd /home/Snakefiles/Illumina && snakemake; /home/Scripts/copy_log.sh"'
    os.system(short_read)
#LONG READS: DEMULTIPLEXING + TRIMMING----------------------------------------------------------------------
    os.system('sh ./Scripts/Long_read/01_demultiplex.sh '+MinIon+' '+Results+'/Long_reads '+options["Threads"])
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
