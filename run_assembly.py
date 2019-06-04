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
from datetime import date
#===========================================================================================================

#GENERAL====================================================================================================
#FETCH OS-TYPE----------------------------------------------------------------------------------------------
system=platform.platform()
if "Windows" in system:
    sys="Windows"
    print("\nWindows based system detected ({})\n".format(system))
    # check if HyperV is enabled (indication of docker Version, used to give specific tips on preformance increase)
    HV = subprocess.Popen('powershell.exe get-service | findstr vmcompute', shell=True, stdout=subprocess.PIPE) 
    for line in HV.stdout:  
        if "Running" in line.decode("utf-8"):
            HyperV="True" 
        else: 
            HyperV="False" 
else:
    sys="UNIX"
    print("\nUNIX based system detected ({})\n".format(system))
#FIND SCRIPTS FOLDER LOCATION-------------------------------------------------------------------------------
options = {}
options["Scripts"] = os.path.dirname(os.path.realpath(__file__)) + "/Scripts"
#GET RUN DATE-----------------------------------------------------------------------------------------------
options["Run"] = date.today().strftime("%Y%m%d")
#===========================================================================================================

#FUNCTIONS==================================================================================================
#INPUT------------------------------------------------------------------------------------------------------
#PATH CORRECTION--------------------------------------------------------------------------------------------
def correct_path(dictionairy):
    global options
    options_copy = dictionairy
    options = {}
    for key, value in options_copy.items():
        options[key] = value
        if sys=="Windows":
            #print("\nConverting Windows paths for use in Docker:")
            for i in list(string.ascii_lowercase+string.ascii_uppercase):
                options[key] = value
                if value.startswith(i+":/"):
                    options[key+"_m"] = value.replace(i+":/","/"+i.lower()+"//").replace('\\','/')
                elif value.startswith(i+":\\"):
                    options[key+"_m"] = value.replace(i+":\\","/"+i.lower()+"//").replace('\\','/')
            #print(" - "+ key +" location ({}) changed to: {}".format(str(options[key][value]),str(options[key+"_m"][value])))
        else:
            options[key+"_m"] = value
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
#INPUT------------------------------------------------------------------------------------------------------
print("ANALYSIS TYPE"+"="*67)
print(" - For short read assembly, input: '1' or 'short' \
    \n - For long read assembly, input: '2' or 'long' \
    \n - For hybrid assembly, input: '3' or 'hybrid'")
analysis = input("\nInput analysis type here: ")
print("="*80)
#SAVE INPUT-------------------------------------------------------------------------------------------------
if analysis == "1" or "short":
    options["Analysis"] = "short"
elif analysis == "2" or "long":
    options["Analysis"] = "long"
elif analysis == "3" or "hybrid":
    options["Analysis"] = "hybrid"
#===========================================================================================================

#SHORT READ ONLY ASSEMBLY===================================================================================
if analysis == "1" or analysis == "short":
#GET INPUT--------------------------------------------------------------------------------------------------
    print("\nSHORT READ ASSEMBLY"+"="*61+"\nOPTIONS"+"-"*73)
    options["Illumina"] = input("Input location of Illumina sample files here: \n")
    options["Results"] = input("Input location to store the results here \n")
    options["Threads"] = str(input("Input number of threads here: \n"))
#CREATE REQUIRED FOLDERS IF NOT EXIST-----------------------------------------------------------------------
    folders = [options["Results"]+"/Short_reads",]
    for i in folders:
        if not os.path.exists(i):
            os.mkdir(i)
#CONVERT MOUNT_PATHS (INPUT) IF REQUIRED--------------------------------------------------------------------    
    correct_path(options)
    #print(options)
#SAVE INPUT TO FILE-----------------------------------------------------------------------------------------
    loc = open(options["Results"]+"/environment.txt", mode="w")
    for key, value in options.items():
        if not key == "Threads":
            loc.write(key+"="+value+"\n")
        else:
            loc.write(key+"="+value)  
    loc.close()
#CREATE ILLUMINA SAMPLE LIST + WRITE TO FILE----------------------------------------------------------------
    file = open(options["Results"]+"/Short_reads/sampleList.txt",mode="w")
    for i in sample_list(options["Illumina"]):
        file.write(i+"\n")
    file.close()
#SHORT READS: SNAKEMAKE CMD----------------------------------------------------------------------------------
    snake = 'docker run -it --rm \
        --name snakemake \
        --cpuset-cpus="0" \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "'+options["Results_m"]+':/home/Pipeline/" \
        -v "'+options["Scripts_m"]+':/home/Scripts/" \
        christophevde/snakemake:v2.2_stable \
        /bin/bash -c "cd /home/Snakemake/ && snakemake; \
        dos2unix /home/Scripts/copy_snakemake_log.sh && sh /home/Scripts/copy_snakemake_log.sh"'
#SHORT READS: RUN PIPELINE - RAWDATA AND RESULTS FOLDER ARE THE SAME-----------------------------------------
    if options["Illumina"] == options["Results"]:
        move = 'docker run -it --rm \
            --name copy_rawdata \
            -v "'+options["Illumina_m"]+':/home/rawdata/" \
            -v "'+options["Scripts_m"]+':/home/Scripts/" \
            christophevde/ubuntu_bash:v2.2_stable \
            /bin/bash -c \
            "dos2unix /home/Scripts/Short_read/01_move_rawdata.bash \
            && sh /home/Scripts/Short_read/01_move_rawdata.bash ' + options["Analysis"]+'"'
        os.system(move)
        os.system(snake)
        delete = 'docker run -it --rm \
            --name copy_rawdata \
            -v "'+options["Illumina_m"]+':/home/rawdata/" \
            -v "'+options["Scripts_m"]+':/home/Scripts/" \
            christophevde/ubuntu_bash:v2.2_stable \
            /bin/bash -c \
            "dos2unix home/Scripts/Short_read/02_delete_rawdata.bash \
            && sh home/Scripts/Short_read/02_delete_rawdata.bash ' + options["Analysis"]+'"'
        os.system(delete)
    #SHORT READS: RUN PIPELINE - RAWDATA AND RESULTS FOLDER ARE DIFFERENT---------------------------------------
    else:
        copy = 'docker run -it --rm \
            --name copy_rawdata \
            -v "'+options["Scripts_m"]+':/home/Scripts/" \
            -v "'+options["Illumina_m"]+':/home/rawdata/" \
            -v "'+options["Results_m"]+':/home/Pipeline/" \
            christophevde/ubuntu_bash:v2.2_stable \
            /bin/bash -c \
            "dos2unix /home/Scripts/Short_read/01_copy_rawdata.bash \
            && sh /home/Scripts/Short_read/01_copy_rawdata.bash ' + options["Analysis"]+'"'
        os.system(copy)
        os.system(snake)
#===========================================================================================================

#LONG READ ONLY ASSEMBLY====================================================================================
elif analysis == "2" or analysis == "long":
#GET INPUT--------------------------------------------------------------------------------------------------
    print("\nLong read assembly selected.")
    options["MinIon"] = input("Input location of MinIon sample files here: \n")
    options["Results"] = input("Input location to store the results here : \n")
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
    options["MinIon"] = input("Input location of MinIon sample files here: \n")
    options["Illumina"] = input("Input location of Illumina sample files here: \n")
    options["Results"] = input("Input location to store the results here \n")
    options["Threads"] = str(input("Input number of threads here: \n"))
    advanced = input("Go to advanced options? (y/n): ").lower()
    if advanced == "y" or advanced =="yes":
        print("ADVANCED OPTIONS"+"-"*64)
#CREATE REQUIRED FOLDERS IF NOT EXIST-----------------------------------------------------------------------
    folders = [options["Results"]+"/Hybrid/"+options["Run"],]
    for i in folders:
        os.makedirs(i, exist_ok=True)
#CONVERT MOUNT_PATHS (INPUT) IF REQUIRED--------------------------------------------------------------------
    correct_path(options)
#SAVE INPUT TO FILE-----------------------------------------------------------------------------------------
    loc = open(options["Results"]+"/Hybrid/"+options["Run"]+"/environment.txt", mode="w")
    for key, value in options.items():
        if not key == "Threads":
            loc.write(key+"="+value+"\n")
        else:
            loc.write(key+"="+value)  
    loc.close()
#CREATE ILLUMINA SAMPLE LIST + WRITE TO FILE----------------------------------------------------------------
    file = open(options["Results"]+"/Hybrid/"+options["Run"]+"/sampleList.txt",mode="w")
    for i in sample_list(options["Illumina"]):
        file.write(i+"\n")
    file.close()
#COPY ILLUMINA SAMPLES TO RESULTS---------------------------------------------------------------------------
    print("[STARTING] Hybrid assembly preparation: Short reads")
    copy = 'docker run -it --rm \
        --name copy_rawdata \
        -v "'+options["Illumina_m"]+':/home/rawdata/" \
        -v "'+options["Results_m"]+':/home/Pipeline/" \
        -v "'+options["Scripts_m"]+':/home/Scripts/" \
        christophevde/ubuntu_bash:v2.2_stable \
        /bin/bash -c "dos2unix /home/Scripts/Hybrid/Short_read/01_copy_rawdata.sh \
        && sh /home/Scripts/Hybrid/Short_read/01_copy_rawdata.sh '+options["Run"]+'"'
    os.system(copy)
#SHORT READS: TRIMMING & QC (DOCKER)------------------------------------------------------------------------
    short_read = 'docker run -it --rm \
        --name snakemake \
        --cpuset-cpus="0" \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v "'+options["Scripts_m"]+':/home/Scripts/" \
        -v "'+options["Results_m"]+':/home/Pipeline/" \
        christophevde/snakemake:v2.3_stable \
        /bin/bash -c "cd /home/Scripts/Hybrid/Short_read && snakemake; \
        dos2unix /home/Scripts/Hybrid/Short_read/03_copy_snakemake_log.sh \
        && sh /home/Scripts/Hybrid/Short_read/03_copy_snakemake_log.sh '+options["Run"]+'"'
    os.system(short_read)
#LONG READS: DEMULTIPLEXING (GUPPY)-------------------------------------------------------------------------
    print("\n[STARTING] Hybrid assembly preparation: Long reads")
    print("\nDemultiplexing Long reads")
    os.system('sh ./Scripts/Hybrid/Long_read/01_demultiplex.sh ' +options["MinIon"]+' '+options["Results"]+' '+options["Threads"])
#LONG READS: QC (PYCOQC)------------------------------------------------------------------------------------
#LONG READS: DEMULTIPLEXING + TRIMMING (PORECHOP)-----------------------------------------------------------
#HYBRID ASSEMBLY--------------------------------------------------------------------------------------------
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
