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
#FETCH OS-TYPE----------------------------------------------------------------------------------------------
system = platform.system()
if "Windows" in system:
    system = "Windows"
    print("\nWindows based system detected ({})\n".format(system))
    # check if HyperV is enabled (indication of docker Version, used to give specific tips on preformance increase)
    HV = subprocess.Popen('powershell.exe get-service | findstr vmcompute', shell=True, stdout=subprocess.PIPE) 
    for line in HV.stdout:  
        if "Running" in line.decode("utf-8"):
            HyperV="True" 
        else: 
            HyperV="False" 
else:
    system="UNIX"
    print("\nUNIX based system detected ({})\n".format(system))
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
        elif "MinIon_fast5=" in line:
            options["MinIon_fast5"] = line.replace('MinIon_fast5=','').replace('\n','')
        elif "MinIon_fastq=" in line:
            options["MinIon_fastq"] = line.replace('MinIon_fastq=','').replace('\n','')
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
    for key, value in options_copy.items():
        options[key] = value
        if system=="Windows":
            #print("\nConverting Windows paths for use in Docker:")
            for i in list(string.ascii_lowercase+string.ascii_uppercase):
                options[key] = value
                if value.startswith(i+":/"):
                    options[key+"_m"] = value.replace(i+":/","/"+i.lower()+"//").replace('\\','/')
                elif value.startswith(i+":\\"):
                    options[key+"_m"] = value.replace(i+":\\","/"+i.lower()+"//").replace('\\','/')
            #print(" - "+ key +" location ({}) changed to: {}".format(str(options[key][value]),str(options[key+"_m"][value])))
        else:
            if key != "Threads" and key != "Run" and key != "Analysis" and key != "Group" and key != "Barcode_kit":
                options[key+"_m"] = value
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

#ANALYSIS TYPE==============================================================================================
#INPUT------------------------------------------------------------------------------------------------------
print("ANALYSIS TYPE"+"="*87)
print(" - For short read assembly, input: '1' or 'short' \
    \n - For long read assembly, input: '2' or 'long' \
    \n - For hybrid assembly, input: '3' or 'hybrid'")
analysis = input("\nInput analysis type here: ")
print("="*100)
#SAVE INPUT-------------------------------------------------------------------------------------------------
options = {}
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
    print("\n[LONG READ ASSEMBLY] SETTINGS"+"="*71)
    try:
        settings = sys.argv[2]
    except:
    #ASK FOR SETTINGS FILE----------------------------------------------------------------------------------
        question = input("Do you have a premade settings-file that you want to use? (y/n) \
            \nPress 'n' to automatically create your own settings-file using the questions asked by this script: ").lower()
        if question == "y":
            settings = input("\nInput location of settings-file here: \n")
        #PARSE FILE
            print("\nParsing settings file")
            settings_parse(settings)
            #convert paths if needed --> function
            #append converted paths to settings-file --> function
            print("Done")
        elif question == "n":
    #REQUIRED INPUT----------------------------------------------------------------------------------------
            settings = ''
            print("\nLONG READS"+'-'*90)
            options["MinIon_fast5"] = input("Input location of MinIon sample files (fast5-format) here: \n")   
            options["MinIon_fastq"] = input("Input location of MinIon sample files (fastq-format) here: \n") 
            print("\nRESULTS"+'-'*93)
            options["Results"] = input("Input location to store the results here \n")
            options["Scripts"] = os.path.dirname(os.path.realpath(__file__)) + "/Scripts"
            options["Run"] = date.today().strftime("%Y%m%d")
    #OPTIONAL INPUT----------------------------------------------------------------------------------------
            print("\n[LONG READS ASSEMBLY] OPTIONAL SETTINGS"+"="*61)
            advanced = input("Show optional settings? (y/n): ").lower()
            if advanced == "y" or advanced =="yes":
                options["Start_genes"] = input("\nInput location of multifasta containing start genes to search for: \n")
                options["Barcode_kit"] = input("Input the ID of the used barcoding kit: \n")
                options["Threads"] = str(input("Input number of threads here: \n"))
#CREATE REQUIRED FOLDERS IF NOT EXIST-----------------------------------------------------------------------
    folders = [options["Results"]+"/Long_reads/"+options["Run"],]
    for i in folders:
        os.makedirs(i, exist_ok=True)
#CONVERT MOUNT_PATHS (INPUT) IF REQUIRED--------------------------------------------------------------------
    correct_path(options)
#SAVE INPUT TO FILE-----------------------------------------------------------------------------------------
    if not settings == '':
        #read content of file (apparently read&write can't happen at the same time)
        loc = open(settings, 'r')
        content = loc.read()
        #print(content)
        loc.close()
        #append converted paths to file
        loc = open(settings, 'a')
        if not "#CONVERTED PATHS" in content:
            loc.write("\n\n#CONVERTED PATHS"+'='*92)
            for key, value in options.items():
                if not key in content:
                    if key == "Illumina_m" or key == "MinIon_fast5_m" or key == "MinIon_fastq_m" or key == "Results_m" or key == "Start_genes_m":
                        loc.write('\n'+key+'='+value)
            loc.write("\n"+'='*108)          
        loc.close()
    else:
        loc = open(options["Results"]+"/Long_reads/"+options["Run"]+"/environment.txt", "w")
        for key, value in options.items():
            if not key == "Threads":
                loc.write(key+"="+value+"\n")
            else:
                loc.write(key+"="+value)  
        loc.close()
#MOVE (AND RENAME) ... TO ... FOLDER------------------------------------------------------------------------
    shutil.copy(options["Start_genes"], options["Results"]+"/Long_reads/"+options["Run"]+"/start_genes.fasta")
    #settings-file to results-folder#LONG READS: DEMULTIPLEXING (GUPPY)-------------------------------------
    print("\n[STARTING] Long read assembly: preparation")
    print("\nDemultiplexing Long reads")
    my_file = Path(options["Results"]+"/Long_reads/"+options["Run"]+"/01_Demultiplex/barcoding_summary.txt")
    if not my_file.is_file():
        #file doesn't exist -> guppy demultiplex hasn't been run
        if system == "UNIX":
            os.system("dos2unix "+options["Scripts"]+"/Long_read/01_demultiplex.sh")
        os.system('sh ./Scripts/Long_read/01_demultiplex.sh '\
            +options["MinIon_fastq"]+' '\
            +options["Results"]+' '\
            +options["Run"]+' '\
            +options["Threads"])
        print("Done")
    else:
        print("Results already exist, nothing to be done")
#LONG READS: QC (PYCOQC)------------------------------------------------------------------------------------
    print("\nPerforming QC on Long reads")
    if not os.path.exists(options["Results"]+"/Long_reads/"+options["Run"]+"/02_QC/"):
        os.makedirs(options["Results"]+"/Long_reads/"+options["Run"]+"/02_QC/")
    my_file = Path(options["Results"]+"/Long_reads/"+options["Run"]+"/02_QC/QC_Long_reads.html")
    if not my_file.is_file():
        #file doesn't exist -> pycoqc hasn't been run
        if system == "UNIX":
            os.system("dos2unix "+options["Scripts"]+"/Long_read/02_pycoQC.sh") 
        os.system('sh ./Scripts/Long_read/02_pycoQC.sh '\
            +options["MinIon_fast5"]+' '\
            +options["Results"]+'/Long_reads/'+options["Run"]+' '\
            +options["Threads"])
        print("Done")
    else:
        print("Results already exist, nothing to be done")
#LONG READS: DEMULTIPLEXING + TRIMMING (PORECHOP)-----------------------------------------------------------
    print("\nTrimming Long reads")
    my_file = Path(options["Results"]+"/Long_reads/"+options["Run"]+"/02_QC/demultiplex_summary.txt")
    if not my_file.is_file():
        #file doesn't exist -> porechop trimming hasn't been run
        if system == "UNIX":
            os.system("dos2unix "+options["Scripts"]+"/Long_read/03_Trimming.sh")
        #demultiplex correct + trimming 
        os.system('sh '+options["Scripts"]+'/Long_read/03_Trimming.sh '\
            +options["Results"]+'/Long_reads/'+options["Run"]+'/01_Demultiplex '\
            +options["Results"]+' '\
            +options["Run"]+' '\
            +options["Threads"])
        #creation of summary table of demultiplexig results (guppy and porechop)
        os.system("python3 "+options["Scripts"]+"/Long_read/04_demultiplex_compare.py "\
            +options["Results"]+"/Long_reads/"+options["Run"]+"/01_Demultiplex/ "\
            +options["Results"]+"/Long_reads/"+options["Run"]+"/03_Trimming/ "\
            +options["Results"]+"/Long_reads/"+options["Run"]+"/02_QC/")
    else:
        print("Results already exist, nothing to be done")
    print("[COMPLETED] Hybrid assembly preparation: Long reads")
#LONG READ ASSEMBLY--------------------------------------------------------------------------------------------
    if system == "UNIX":
        os.system("dos2unix "+options["Scripts"]+"/Long_read/05_Unicycler.sh")
    print("\n[STARTING] Unicycler: Long read assembly")
    for bc in os.listdir(options["Results"]+"/Long_reads/"+options["Run"]+"/03_Trimming/"):
        bc = bc.replace('.fastq.gz','')
        if "BC" in bc:
            print("Starting assembly for barcode: "+bc)
            my_file = Path(options["Results"]+"/Long_reads/"+options["Run"]+"/04_Assembly/"+bc+"/assembly.fasta")
            if not my_file.is_file():
                #file doesn't exist -> unicycle hasn't been run
                os.system('sh ./Scripts/Long_read/05_Unicycler.sh '\
                    +options["Results"]+'/Long_reads/'+options["Run"]+' '\
                    +bc+' '\
                    +options["Threads"])
            else:
                print("Results already exist for barcode: "+bc+", nothing to be done")
#BANDAGE----------------------------------------------------------------------------------------------------
    print("Bandage is an optional step used to visualise and correct the created assemblys, and is completely manual")
    Bandage = input("Do you wan't to do a Bandage visualisalisation? (y/n)").lower()
    if Bandage == "y":
        Bandage_done = input("[WAITING] If you're done with Bandage input 'y' to continue: ").lower()
        while Bandage_done != 'y':
            Bandage_done = input("[WAITING] If you're done with Bandage input 'y' to continue: ").lower()
    elif Bandage == "n":
        print("skipping Bandage step")
#PROKKA-----------------------------------------------------------------------------------------------------

#===========================================================================================================

#HYBRID ASSEMBLY============================================================================================
elif analysis == "3" or analysis == "hybrid":
#GET INPUT--------------------------------------------------------------------------------------------------
    print("\n[HYBRID ASSEMBLY] SETTINGS"+"="*74)
    try:
        settings = sys.argv[2]
    except:
    #ASK FOR SETTINGS FILE----------------------------------------------------------------------------------
        question = input("Do you have a premade settings-file that you want to use? (y/n) \
            \nPress 'n' to automatically create your own settings-file using the questions asked by this script: ").lower()
        if question == "y":
            settings = input("\nInput location of settings-file here: \n")
        #PARSE FILE
            print("\nParsing settings file")
            settings_parse(settings)
            #convert paths if needed --> function
            #append converted paths to settings-file --> function
            print("Done")
        elif question == "n":
    #REQUIRED INPUT----------------------------------------------------------------------------------------
            settings = ''
            print("\nSHORT READS"+'-'*89)
            options["Illumina"] = input("Input location of Illumina sample files here: \n")
            print("\nLONG READS"+'-'*90)
            options["MinIon_fast5"] = input("Input location of MinIon sample files (fast5-format) here: \n")   
            options["MinIon_fastq"] = input("Input location of MinIon sample files (fastq-format) here: \n") 
            print("\nRESULTS"+'-'*93)
            options["Results"] = input("Input location to store the results here \n")
            print("SAMPLE INFO")
            options["Cor_samples"] = input("Input location of text file containing info on wich Illumina samples correspond with which MinIon barcode: \n")
            options["Scripts"] = os.path.dirname(os.path.realpath(__file__)) + "/Scripts"
            options["Run"] = date.today().strftime("%Y%m%d")
    #OPTIONAL INPUT----------------------------------------------------------------------------------------
            print("\n[HYBRID ASSEMBLY] OPTIONAL SETTINGS"+"="*65)
            advanced = input("Show optional settings? (y/n): ").lower()
            if advanced == "y" or advanced =="yes":
                options["Start_genes"] = input("\nInput location of multifasta containing start genes to search for: \n")
                options["Barcode_kit"] = input("Input the ID of the used barcoding kit: \n")
                options["Threads"] = str(input("Input number of threads here: \n"))
#CREATE REQUIRED FOLDERS IF NOT EXIST-----------------------------------------------------------------------
    folders = [options["Results"]+"/Hybrid/"+options["Run"],]
    for i in folders:
        os.makedirs(i, exist_ok=True)
#CONVERT MOUNT_PATHS (INPUT) IF REQUIRED--------------------------------------------------------------------
    correct_path(options)
#SAVE INPUT TO FILE-----------------------------------------------------------------------------------------
    if not settings == '':
        #read content of file (apparently read&write can't happen at the same time)
        loc = open(settings, 'r')
        content = loc.read()
        #print(content)
        loc.close()
        #append converted paths to file
        loc = open(settings, 'a')
        if not "#CONVERTED PATHS" in content:
            loc.write("\n\n#CONVERTED PATHS"+'='*92)
            for key, value in options.items():
                print(options)
                if not key in content:
                    print(key)
                    if key == "Illumina_m" or key == "MinIon_fast5_m" or key == "MinIon_fastq_m" or key == "Results_m" or key == "Start_genes_m":
                        loc.write('\n'+key+'='+value)
            loc.write("\n"+'='*108)          
        loc.close()
    else:
        loc = open(options["Results"]+"/Hybrid/"+options["Run"]+"/environment.txt", mode="w")
        for key, value in options.items():
            if not key == "Threads":
                loc.write(key+"="+value+"\n")
            else:
                loc.write(key+"="+value)  
        loc.close()
#MOVE (AND RENAME) ... TO ... FOLDER------------------------------------------------------------------------
    shutil.move(options["Cor_samples"], options["Results"]+"/Hybrid/"+options["Run"]+"/corresponding_samples.txt")
    shutil.copy(options["Start_genes"], options["Results"]+"/Hybrid/"+options["Run"]+"/start_genes.fasta")
    #settings-file to results-folder
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
    my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/01_Demultiplex/barcoding_summary.txt")
    if not my_file.is_file():
        #file doesn't exist -> guppy demultiplex hasn't been run
        if system == "UNIX":
            os.system("dos2unix "+options["Scripts"]+"/Hybrid/Long_read/01_demultiplex.sh")
        os.system('sh ./Scripts/Hybrid/Long_read/01_demultiplex.sh '\
            +options["MinIon_fastq"]+' '\
            +options["Results"]+' '\
            +options["Run"]+' '\
            +options["Threads"])
        print("Done")
    else:
        print("Results already exist, nothing to be done")
#LONG READS: QC (PYCOQC)------------------------------------------------------------------------------------
    print("\nPerforming QC on Long reads")
    if not os.path.exists(options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/02_QC/"):
        os.makedirs(options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/02_QC/")
    my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/02_QC/QC_Long_reads.html")
    if not my_file.is_file():
        #file doesn't exist -> pycoqc hasn't been run
        if system == "UNIX":
            os.system("dos2unix "+options["Scripts"]+"/Hybrid/Long_read/02_pycoQC.sh") 
        os.system('sh ./Scripts/Hybrid/Long_read/02_pycoQC.sh '\
            +options["MinIon_fast5"]+' '\
            +options["Results"]+'/Hybrid/'+options["Run"]+' '\
            +options["Threads"])
        print("Done")
    else:
        print("Results already exist, nothing to be done")
#LONG READS: DEMULTIPLEXING + TRIMMING (PORECHOP)-----------------------------------------------------------
    print("\nTrimming Long reads")
    my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/02_QC/demultiplex_summary.txt")
    if not my_file.is_file():
        #file doesn't exist -> porechop trimming hasn't been run
        if system == "UNIX":
            os.system("dos2unix "+options["Scripts"]+"/Hybrid/Long_read/03_Trimming.sh")
        #demultiplex correct + trimming 
        os.system('sh '+options["Scripts"]+'/Hybrid/Long_read/03_Trimming.sh '\
            +options["Results"]+'/Hybrid/'+options["Run"]+'/02_Long_reads/01_Demultiplex '\
            +options["Results"]+' '\
            +options["Run"]+' '\
            +options["Threads"])
        #creation of summary table of demultiplexig results (guppy and porechop)
        os.system("python3 "+options["Scripts"]+"/Hybrid/Long_read/04_demultiplex_compare.py "\
            +options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/01_Demultiplex/ "\
            +options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/03_Trimming/ "\
            +options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/02_QC/")
    else:
        print("Results already exist, nothing to be done")
    print("[COMPLETED] Hybrid assembly preparation: Long reads")
#HYBRID ASSEMBLY--------------------------------------------------------------------------------------------
    if system == "UNIX":
        os.system("dos2unix "+options["Scripts"]+"/Long_read/05_Unicycler.sh")
    print("\n[STARTING] Unicycler: hybrid assembly")
    os.system('python3 ./Scripts/Hybrid/01_Unicycler.py '\
        +options["Results"]+'/Hybrid/'+options["Run"]+'/01_Short_reads '\
        +options["Results"]+'/Hybrid/'+options["Run"]+'/02_Long_reads/03_Trimming '\
        +options["Results"]+'/Hybrid/'+options["Run"]+'/03_Assembly '\
        +options["Results"]+'/Hybrid/'+options["Run"]+'/corresponding_samples.txt '\
        +options["Results"]+'/Hybrid/'+options["Run"]+'/start_genes.fasta '\
        +options["Threads"])
#BANDAGE----------------------------------------------------------------------------------------------------
    print("Bandage is an optional step used to visualise and correct the created assemblys, and is completely manual")
    Bandage = input("Do you wan't to do a Bandage visualisalisation? (y/n)").lower()
    if Bandage == "y":
        Bandage_done = input("[WAITING] If you're done with Bandage input 'y' to continue: ").lower()
        while Bandage_done != 'y':
            Bandage_done = input("[WAITING] If you're done with Bandage input 'y' to continue: ").lower()
    elif Bandage == "n":
        print("skipping Bandage step")
#PROKKA-----------------------------------------------------------------------------------------------------

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
