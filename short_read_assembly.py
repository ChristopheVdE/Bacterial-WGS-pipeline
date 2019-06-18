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
from pathlib import Path
import shutil
import sys
#===========================================================================================================

#GENERAL====================================================================================================
print("Please wait while the Script fetches some system info:")
#FETCH OS-TYPE----------------------------------------------------------------------------------------------
system=platform.system()
if "Windows" in system:
    system = "Windows"
    print("  - Windows based system detected ({})".format(system))
    # check if HyperV is enabled (indication of docker Version, used to give specific tips on preformance increase)
    HV = subprocess.Popen('powershell.exe get-service | findstr vmcompute', shell=True, stdout=subprocess.PIPE) 
    for line in HV.stdout:  
        if "Running" in line.decode("utf-8"):
            HyperV="True" 
        else: 
            HyperV="False"
elif "Darwin" in system:
    system = "MacOS"
    print("  - MacOS based system detected ({})".format(system))
else:
    system = "UNIX"
    print("  - UNIX based system detected ({})".format(system))
#LINUX OS: GET USER ID AND GROUP ID-------------------------------------------------------------------------
# if system == "UNIX":
#     UID = subprocess.Popen('id -u', shell=True, stdout=subprocess.PIPE)
#     for line in UID.stdout:
#         UID = line.decode("utf-8")
#     GID = subprocess.Popen('id -g', shell=True, stdout=subprocess.PIPE) 
#     for line in GID.stdout:
#         GID = line.decode("utf-8")
#     options["Group"] = UID+":"+GID
#===========================================================================================================

# GET MAX THREADS===========================================================================================
    # For windows, the threads avaible to docker are already limited by the virtualisation program. 
    # This means that the total ammount of threads avaiable on docker is only a portion of the threads avaiable to the host
    # --> no extra limitation needed
    # Linux/Mac doesn't use a virutalisation program.
    # The number of threads available to docker should be the same as the total number of threads available on the HOST
    # --> extra limitation is needed in order to not slow down the PC to much (reserve CPU for host)
# TOTAL THREADS OF HOST-------------------------------------------------------------------------------------
print("  - Fetching amount of threads on system")
if system == "Windows":
    host = subprocess.Popen('WMIC CPU Get NumberOfLogicalProcessors', shell=True, stdout=subprocess.PIPE)
elif system == "MacOS":
    host = subprocess.Popen('sysctl -n hw.ncpu', shell=True, stdout=subprocess.PIPE)
else:
    host = subprocess.Popen('nproc --all', shell=True, stdout=subprocess.PIPE)

for line in host.stdout:
    # linux only gives a number, Windows gives a text line + a number line
    if any(i in line.decode("UTF-8") for i in ("0","1","2","3","4","5","6","7","8","9")):
        h_threads = int(line.decode("UTF-8"))
# MAX THREADS AVAILABLE IN DOCKER----------------------------------------------------------------------------
docker = subprocess.Popen('docker run -it --rm --name ubuntu_bash christophevde/ubuntu_bash:v2.0_stable nproc --all', shell=True, stdout=subprocess.PIPE)
for line in docker.stdout:
    d_threads = int(line.decode("UTF-8"))
# SUGESTED THREADS FOR ANALYSIS CALCULATION-----------------------------------------------------------------
if system=="UNIX":
    if h_threads < 5:
        s_threads = h_threads//2
    else:
        s_threads = h_threads//4*3
else:
    s_threads = d_threads
print("Done\n")
#===========================================================================================================

#FUNCTIONS==================================================================================================
#SETTINGS FILE PARSING--------------------------------------------------------------------------------------
def settings_parse(settings):
    file = open(settings,'r')
    global options
    global analysis
    options = {}
    for line in file:
        if  "Illumina=" in line:
            options["Illumina"] = line.replace('Illumina=','').replace('\n','')
        elif "MinIon=" in line:
            options["MinIon"] = line.replace('MinIon=','').replace('\n','')
        elif "Results=" in line:
            options["Results"] = line.replace('Results=','').replace('\n','')
        elif "Adaptors=" in line:
            options["Adaptors"] = line.replace('Adaptors=','').replace('\n','')
        elif "Barcode_kit=" in line:
            options["Barcode_kit"] = line.replace('Barcode_kit=','').replace('\n','')
        elif "Threads=" in line:
            options["Threads"] = line.replace('Threads=','').replace('\n','')
        elif "Start_genes" in line:
            options["Start_genes"] = line.replace('Start_genes=','').replace('\n','')
    options["Run"] = date.today().strftime("%Y%m%d")
    options["Scripts"] = os.path.dirname(os.path.realpath(__file__)) + "/Scripts"
    file.close()
    return options
#PATH CORRECTION--------------------------------------------------------------------------------------------
def correct_path(dictionairy):
    global options
    options_copy = dictionairy
    options = {}
    not_convert = ["Threads", "Run", "Analysis", "Group", "Barcode_kit", "Genus", "Species", "Kingdom"]
    if system == "Windows":
        print("\nConverting Windows paths for use in Docker:")
        for key, value in options_copy.items():
            options[key] = value
            for i in list(string.ascii_lowercase+string.ascii_uppercase):
                options[key] = value
                if value.startswith(i+":/"):
                    options[key+"_m"] = value.replace(i+":/","/"+i.lower()+"//").replace('\\','/')
                elif value.startswith(i+":\\"):
                    options[key+"_m"] = value.replace(i+":\\","/"+i.lower()+"//").replace('\\','/')
            print(" - "+ key +" location ({}) changed to: {}".format(str(options[key]),str(options[key+"_m"])))
    else:
        print("\nUNIX paths shouldn't require a conversion for use in Docker:")
        for key, value in options_copy.items():
            options[key] = value
            if not key in not_convert:
                options[key+"_m"] = value
                print(" - "+ key +" location ({}) changed to: {}".format(str(options[key]),str(options[key+"_m"])))
        return options
#SAVING INPUT TO FILE---------------------------------------------------------------------------------------
#SHORT READ SAMPLE LIST CREATION----------------------------------------------------------------------------
def sample_list(Illumina):
    global ids
    ids =[]
    for sample in os.listdir(Illumina):
        if ".fastq.gz" in sample:
            ids.append(sample.replace('_L001_R1_001.fastq.gz','').replace('_L001_R2_001.fastq.gz',''))
    ids = sorted(set(ids))
    return ids
#===========================================================================================================

#SHORT READ ONLY ASSEMBLY===================================================================================
#GET INPUT--------------------------------------------------------------------------------------------------
print("\nSHORT READ ASSEMBLY"+"="*61+"\nOPTIONS"+"-"*73)
options["Illumina"] = input("Input location of Illumina sample files here: \n")
options["Results"] = input("Input location to store the results here \n")
options["Threads"] = str(input("Input number of threads here: \n"))
options["Scripts"] = os.path.dirname(os.path.realpath(__file__)) + "/Scripts"
options["Run"] = date.today().strftime("%Y%m%d")
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
    dos2unix -q /home/Scripts/copy_snakemake_log.sh && sh /home/Scripts/copy_snakemake_log.sh"'
#SHORT READS: RUN PIPELINE - RAWDATA AND RESULTS FOLDER ARE THE SAME-----------------------------------------
if options["Illumina"] == options["Results"]:
    move = 'docker run -it --rm \
        --name copy_rawdata \
        -v "'+options["Illumina_m"]+':/home/rawdata/" \
        -v "'+options["Scripts_m"]+':/home/Scripts/" \
        christophevde/ubuntu_bash:v2.2_stable \
        /bin/bash -c \
        "dos2unix -q /home/Scripts/Short_read/01_move_rawdata.bash \
        && sh /home/Scripts/Short_read/01_move_rawdata.bash ' + options["Analysis"]+'"'
    os.system(move)
    os.system(snake)
    delete = 'docker run -it --rm \
        --name copy_rawdata \
        -v "'+options["Illumina_m"]+':/home/rawdata/" \
        -v "'+options["Scripts_m"]+':/home/Scripts/" \
        christophevde/ubuntu_bash:v2.2_stable \
        /bin/bash -c \
        "dos2unix -q home/Scripts/Short_read/02_delete_rawdata.bash \
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
        "dos2unix -q /home/Scripts/Short_read/01_copy_rawdata.bash \
        && sh /home/Scripts/Short_read/01_copy_rawdata.bash ' + options["Analysis"]+'"'
    os.system(copy)
    os.system(snake)
#===========================================================================================================