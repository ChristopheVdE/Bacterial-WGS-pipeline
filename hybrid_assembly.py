############################################################################################################
#NAME: hybrid assembly.py
#AUTHOR: Christophe Van den Eynde
#FUNCTION: creates some texts files containing location variables that are used by the snakefile as input
#USAGE LINUX/MAC: python3 hybrid_assembly.py
#USAGE WINDOWS: python.exe hybrid_assembly.py
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

#HYBRID ASSEMBLY============================================================================================
options = {}
#ERROR COLLECTION-------------------------------------------------------------------------------------------
errors = []
error_count = 0
while error_count == 0:
#GET INPUT--------------------------------------------------------------------------------------------------
    print("\n[HYBRID ASSEMBLY] SETTINGS"+"="*74)
    try:
        settings = sys.argv[1]
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
            options["MinIon"] = input("Input location of MinIon sample files here: \n")    
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
                options["Start_genes"] = input("Input location of multifasta containing start genes to search for (unicycler will use these to rotate the contigs so that they start with the start_gene): \n")
                options["Barcode_kit"] = input("Input the ID of the used barcoding kit: \n")
    #THREADS------------------------------------------------------------------------------------------
                print("THREADS"+"-"*101)
                print("\nTotal threads on host: {}".format(h_threads))
                print("Max threads in Docker: {}".format(d_threads))
                print("Suggest ammount of threads to use in the analysis: {}".format(s_threads))
                options["Threads"] = input("\nInput the ammount of threads to use for the analysis below.\
                \nIf you want to use the suggested ammount, just press ENTER (or type in the suggested number)\n")
                if options["Threads"] =='':
                    options["Threads"] = str(s_threads)
                    print("\nChosen to use the suggested ammount of threads. Reserved {} threads for Docker".format(options["Threads"]))
                else:
                    print("\nManually specified the ammount of threads. Reserved {} threads for Docker".format(options["Threads"]))
    #PROKKA INFO (ANNOTATION)---------------------------------------------------------------------------
                print("\nINFO FOR ANNOTATION"+"-"*89)
                options["Genus"] = input("Input the genus of your sequenced organism here: \n")
                options["Species"] = input("Input the species of your sequenced organism here: \n")
                options["Kingdom"] = input("Input the Kingdom of your sequenced organism here: \n")
    #CREATE OPTIONAL SETTINGS KEYS TO PREVENT ERRORS----------------------------------------------------
            else:
                options["Start_genes"] = ''
                options["Barcode_kit"] = ''
                options["Threads"] = str(s_threads)
                options["Genus"] = ''
                options["Species"] = ''
                options["Kingdom"] = ''  
        print('='*108)
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
                    if key == "Illumina_m" or key == "MinIon_m" or key == "Results_m" or key == "Start_genes_m":
                        loc.write('\n'+key+'='+value)
            loc.write("\n"+'='*108)          
        loc.close()
        shutil.move(settings, options["Results"]+"/Hybrid/"+options["Run"]+"/settings.txt")
    else:
        loc = open(options["Results"]+"/Hybrid/"+options["Run"]+"/settings.txt", mode="w")
        for key, value in options.items():
            if not key == "Threads":
                loc.write(key+"="+value+"\n")
            else:
                loc.write(key+"="+value)  
        loc.close()
#MOVE (AND RENAME) ... TO ... FOLDER------------------------------------------------------------------------
    shutil.copy(options["Cor_samples"], options["Results"]+"/Hybrid/"+options["Run"]+"/corresponding_samples.txt")
    if not options["Start_genes"] == '':
        shutil.copy(options["Start_genes"], options["Results"]+"/Hybrid/"+options["Run"]+"/start_genes.fasta")
#CREATE ILLUMINA SAMPLE LIST + WRITE TO FILE----------------------------------------------------------------
    file = open(options["Results"]+"/Hybrid/"+options["Run"]+"/sampleList.txt",mode="w")
    for i in sample_list(options["Illumina"]):
        file.write(i+"\n")
    file.close()
#COPY ILLUMINA SAMPLES TO RESULTS---------------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] Copying rawdata") 
    copy = 'docker run -it --rm \
        --name copy_rawdata \
        -v "'+options["Illumina_m"]+':/home/rawdata/" \
        -v "'+options["Results_m"]+':/home/Pipeline/" \
        -v "'+options["Scripts_m"]+':/home/Scripts/" \
        christophevde/ubuntu_bash:v2.2_stable \
        /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/01_copy_rawdata.sh \
        && sh /home/Scripts/Hybrid/Short_read/01_copy_rawdata.sh '+options["Run"]+'"'
    os.system(copy)
    print("Done")
#SHORT READS: FASTQC RAWDATA (DOCKER)------------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] FastQC rawdata")
    for sample in ids:
        my_file1 = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/01_Short_reads/"+sample+"/01_QC-Rawdata/QC_FastQC/"+sample+"_L001_R1_001_fastqc.html")
        my_file2 = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/01_Short_reads/"+sample+"/01_QC-Rawdata/QC_FastQC/"+sample+"_L001_R1_001_fastqc.html")
        if not my_file1.is_file() and not my_file2.is_file():
            os.system('docker run -it --rm \
                --name fastqc_raw \
                -v "'+options["Scripts_m"]+':/home/Scripts/" \
                -v "'+options["Results_m"]+':/home/Pipeline/" \
                christophevde/fastqc:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC01_FastQC_Raw.sh \
                && /home/Scripts/Hybrid/Short_read/QC01_FastQC_Raw.sh '+sample+' '+options["Run"]+' '+options["Threads"]+'"')
            if not my_file1.is_file() or not my_file2.is_file():
                errors.append("[ERROR] STEP 1: FastQC; quality control rawdata (short reads)")
                error_count +=1
        else:
            print("  - FastQC results for the rawdata of sample "+sample+" already exists")
    print("Done")
#SHORT READS: MULTIQC RAWDATA (DOCKER)-----------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] MultiQC rawdata")
    #FULL RUN------------------------------------------------------------------------------------------------
    my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/01_Short_reads/QC_MultiQC/QC-Rawdata/multiqc_report.html")
    if not my_file.is_file():
        #CREATE TEMP FOLDER----------------------------------------------------------------------------------
        os.makedirs(options["Results"]+"/Hybrid/"+options["Run"]+"/temp/", exist_ok=True)
        #COPY FASTQC RESULTS---------------------------------------------------------------------------------
        print("creating temporary directory to copy all fastqc results of rawdata")
        for sample in ids:
            os.system('docker run -it --rm\
                --name copy_fastqc\
                -v "'+options["Results"]+'/Hybrid/'+options["Run"]+'/01_Short_reads/'+sample+'/01_QC-Rawdata/QC_FastQC/:/home/fastqc" \
                -v "'+options["Results"]+'/Hybrid/'+options["Run"]+'/temp/:/home/multiqc" \
                christophevde/ubuntu_bash:v2.2_stable \
                /bin/bash -c "cp -rn /home/fastqc/* /home/multiqc"')
        #EXECUTE MULTIQC-------------------------------------------------------------------------------------
            os.system('docker run -it --rm \
                --name multiqc_raw \
                -v "'+options["Scripts_m"]+':/home/Scripts/" \
                -v "'+options["Results_m"]+':/home/Pipeline/" \
                christophevde/multiqc:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC01_MultiQC_Raw_FullRun.sh \
                && /home/Scripts/Hybrid/Short_read/QC01_MultiQC_Raw_FullRun.sh '+options["Run"]+'"')
            if not my_file.is_file():
                errors.append("[ERROR] STEP 2: MultiQC; quality control rawdata (short reads)")
                error_count +=1
        else:
            print("  - MultiQC results for the full run (rawdata) already exists")
        #REMOVE TEMP FOLDER----------------------------------------------------------------------------------
        os.system('docker run -it --rm\
            --name delete_temp_folder\
            -v "'+options["Results"]+'/Hybrid/'+options["Run"]+':/home/multiqc" \
            christophevde/ubuntu_bash:v2.2_stable \
            /bin/bash -c "rm -R /home/multiqc/temp"')
    #EACH SAMPLE SEPARALTY-----------------------------------------------------------------------------------
    for sample in ids:
        my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/01_Short_reads/"+sample+"/01_QC-Rawdata/QC_MultiQC/multiqc_report.html")
        if not my_file.is_file():
            os.system('docker run -it --rm \
                --name multiqc_raw \
                -v "'+options["Scripts_m"]+':/home/Scripts/" \
                -v "'+options["Results_m"]+':/home/Pipeline/" \
                christophevde/multiqc:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC01_MultiQC_Raw_oneSample.sh \
                && /home/Scripts/Hybrid/Short_read/QC01_MultiQC_Raw_oneSample.sh '+sample+' '+options["Run"]+'"')
            if not my_file.is_file():
                errors.append("[ERROR] STEP 2: MultiQC; quality control rawdata (short reads)")
                error_count +=1
        else:
            print("  - MultiQC results for the rawdata of sample "+sample+" already exists")
    print("Done")
#SHORT READS: TRIMMING (DOCKER)------------------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] Trimming")
    for sample in ids:
        my_file1 = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/01_Short_reads/"+sample+"/02_Trimmomatic/"+sample+"_L001_R1_001_P.fastq.gz")
        my_file2 = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/01_Short_reads/"+sample+"/02_Trimmomatic/"+sample+"_L001_R2_001_P.fastq.gz")
        if not my_file1.is_file() and not my_file2.is_file():
            os.system('docker run -it --rm \
                --name trimmomatic \
                -v "'+options["Scripts_m"]+':/home/Scripts/" \
                -v "'+options["Results_m"]+':/home/Pipeline/" \
                christophevde/trimmomatic:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/02_runTrimmomatic.sh \
                && /home/Scripts/Hybrid/Short_read/02_runTrimmomatic.sh '+sample+' '+options["Run"]+' '+options["Threads"]+'"')
        if not my_file1.is_file() or not my_file2.is_file():
                errors.append("[ERROR] STEP 3: TRIMMOMATIC; trimming adaptors form reads (short reads)")
                error_count +=1
        else:
            print("  - Trimmomatic results of sample "+sample+" already exists")
    print("Done")
#SHORT READS: FASTQC TRIMMED (DOCKER)------------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] FastQC Trimmed data")
    for sample in ids:
        my_file1 = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/01_Short_reads/"+sample+"/03_QC-Trimmomatic_Paired/QC_FastQC/"+sample+"_L001_R1_001_P_fastqc.html")
        my_file2 = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/01_Short_reads/"+sample+"/03_QC-Trimmomatic_Paired/QC_FastQC/"+sample+"_L001_R1_001_P_fastqc.html")
        if not my_file1.is_file() and not my_file2.is_file():
            os.system('docker run -it --rm \
                --name fastqc_trim \
                -v "'+options["Scripts_m"]+':/home/Scripts/" \
                -v "'+options["Results_m"]+':/home/Pipeline/" \
                christophevde/fastqc:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC02_FastQC_Trim.sh \
                && /home/Scripts/Hybrid/Short_read/QC02_FastQC_Trim.sh '+sample+' '+options["Run"]+' '+options["Threads"]+'"')
            if not my_file1.is_file() or not my_file2.is_file():
                errors.append("[ERROR] STEP 4: FastQC; quality control trimmed data (short reads)")
                error_count +=1
        else:
            print("  - FastQC results for the trimmed data of sample "+sample+" already exists")
    print("Done")
#SHORT READS: MULTIQC TRIMMED (DOCKER)-----------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] MultiQC Trimmed data")
    #FULL RUN------------------------------------------------------------------------------------------------
    my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/01_Short_reads/QC_MultiQC/QC-Trimmed/multiqc_report.html")
    if not my_file.is_file():
    #CREATE TEMP FOLDER--------------------------------------------------------------------------------------
        os.makedirs(options["Results"]+"/Hybrid/"+options["Run"]+"/temp/", exist_ok=True)
        #COPY FASTQC RESULTS---------------------------------------------------------------------------------
        print("creating temporary directory to copy all fastqc results of trimmed data")
        for sample in ids:
            os.system('docker run -it --rm \
                --name copy_fastqc\
                -v "'+options["Results"]+'/Hybrid/'+options["Run"]+'/01_Short_reads/'+sample+'/03_QC-Trimmomatic_Paired/QC_FastQC/:/home/fastqc" \
                -v "'+options["Results"]+'/Hybrid/'+options["Run"]+'/temp/:/home/multiqc" \
                christophevde/ubuntu_bash:v2.2_stable \
                /bin/bash -c "cp -rn /home/fastqc/* /home/multiqc"')
        #EXECUTE MULTIQC-------------------------------------------------------------------------------------
        os.system('docker run -it --rm \
            --name multiqc_trimmed \
            -v "'+options["Scripts_m"]+':/home/Scripts/" \
            -v "'+options["Results_m"]+':/home/Pipeline/" \
            christophevde/multiqc:v2.2_stable \
            /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC02_MultiQC_Trim_FullRun.sh \
            && /home/Scripts/Hybrid/Short_read/QC02_MultiQC_Trim_FullRun.sh '+options["Run"]+'"')
        if not my_file.is_file():
            errors.append("[ERROR] STEP 5: MultiQC; quality control trimmed data (short reads)")
            error_count +=1
        else:
            print("  - MultiQC results for the full run (trimmed data) already exists")
        #REMOVE TEMP FOLDER----------------------------------------------------------------------------------
        os.system('docker run -it --rm \
            --name delete_temp_folder\
            -v "'+options["Results"]+'/Hybrid/'+options["Run"]+':/home/multiqc" \
            christophevde/ubuntu_bash:v2.2_stable \
            /bin/bash -c "rm -R /home/multiqc/temp"')
    #EACH SAMPLE SEPARALTY-----------------------------------------------------------------------------------
    for sample in ids:
        my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/01_Short_reads/"+sample+"/03_QC-Trimmomatic_Paired/QC_MultiQC/multiqc_report.html")
        if not my_file.is_file():
            os.system('docker run -it --rm \
                --name multiqc_raw \
                -v "'+options["Scripts_m"]+':/home/Scripts/" \
                -v "'+options["Results_m"]+':/home/Pipeline/" \
                christophevde/multiqc:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC02_MultiQC_Trim_oneSample.sh \
                && /home/Scripts/Hybrid/Short_read/QC02_MultiQC_Trim_oneSample.sh '+sample+' '+options["Run"]+'"')
            if not my_file.is_file():
                errors.append("[ERROR] STEP 5: MultiQC; quality control rawdata (short reads)")
                error_count +=1
        else:
            print("  - MultiQC results for the trimmed data of sample "+sample+" already exists")
    print("Done")
#LONG READS: DEMULTIPLEXING (GUPPY)-------------------------------------------------------------------------
    print("\n[HYBRID][LONG READS] Guppy: demultiplexing")
    my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/01_Demultiplex/barcoding_summary.txt")
    if not my_file.is_file():
        #file doesn't exist -> guppy demultiplex hasn't been run
        if system == "UNIX":
            os.system("dos2unix -q "+options["Scripts"]+"/Hybrid/Long_read/01_demultiplex.sh")
        os.system('sh ./Scripts/Hybrid/Long_read/01_demultiplex.sh '\
            +options["MinIon"]+'/fastq/pass '\
            +options["Results"]+' '\
            +options["Run"]+' '\
            +options["Threads"])
        if not my_file.is_file():
            errors.append("[ERROR] STEP 6: Guppy demultiplexing failed")
            error_count +=1
    else:
        print("  - Results already exist")
    print("Done")
#LONG READS: QC (PYCOQC)------------------------------------------------------------------------------------
    print("\n[HYBRID][LONG READS] PycoQC: Performing QC on Long reads")
    if not os.path.exists(options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/02_QC/"):
        os.makedirs(options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/02_QC/")
    my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/02_QC/QC_Long_reads.html")
    if not my_file.is_file():
        #file doesn't exist -> pycoqc hasn't been run
        if system == "UNIX":
            os.system("dos2unix -q "+options["Scripts"]+"/Hybrid/Long_read/02_pycoQC.sh") 
        os.system('sh ./Scripts/Hybrid/Long_read/02_pycoQC.sh '\
            +options["MinIon"]+'/fast5/pass '\
            +options["Results"]+'/Hybrid/'+options["Run"]+' '\
            +options["Threads"])
        if not my_file.is_file():
            errors.append("[ERROR] STEP 7: PycoQC quality control failed")
            error_count +=1
    else:
        print("Results already exist")
    print("Done")
#LONG READS: DEMULTIPLEXING + TRIMMING (PORECHOP)-----------------------------------------------------------
    print("\n[HYBRID][LONG READS] Porechop: Trimming Long reads")
    my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/02_Long_reads/02_QC/demultiplex_summary.txt")
    if not my_file.is_file():
        #file doesn't exist -> porechop trimming hasn't been run
        if system == "UNIX":
            os.system("dos2unix -q "+options["Scripts"]+"/Hybrid/Long_read/03_Trimming.sh")
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
        if not my_file.is_file():
            errors.append("[ERROR] STEP 8: Porechop demuliplex correction and trimming failed")
            error_count +=1
    else:
        print("Results already exist")
    print("Done")
#HYBRID ASSEMBLY--------------------------------------------------------------------------------------------
    print("\n[HYBRID][ASSEMBLY] Unicycler: building hybrid assembly")
    os.system('python3 ./Scripts/Hybrid/01_Unicycler.py '\
        +options["Results"]+'/Hybrid/'+options["Run"]+'/01_Short_reads '\
        +options["Results"]+'/Hybrid/'+options["Run"]+'/02_Long_reads/03_Trimming '\
        +options["Results"]+'/Hybrid/'+options["Run"]+'/03_Assembly '\
        +options["Results"]+'/Hybrid/'+options["Run"]+'/corresponding_samples.txt '\
        +options["Results"]+'/Hybrid/'+options["Run"]+'/start_genes.fasta '\
        +options["Threads"])
    # if not my_file.is_file():
    #     errors.append("[ERROR] STEP 9: Unicycler assembly failed")
    #     error_count +=1
    print("Done")
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
    print("\n[HYBRID][ANNOTATION] Prokka: annotating assembly")
    if system == "UNIX":
        os.system("dos2unix -q "+options["Scripts"]+"/Hybrid/02_Prokka.sh")
    for sample in os.listdir(options["Results"]+"/Hybrid/"+options["Run"]+"/03_Assembly/"):
        my_file = Path(options["Results"]+"/Hybrid/"+options["Run"]+"/04_Prokka/"+sample+"/*.gff")
        if not my_file.is_file():
            os.system('sh '+options["Scripts"]+'/Hybrid/02_Prokka.sh '\
                +options["Results"]+'/Hybrid/'+options["Run"]+'/04_Prokka/'+sample+' '\
                +options["Genus"]+' '\
                +options["Species"]+' '\
                +options["Kingdom"]+' '\
                +options["Results"]+'/Hybrid/'+options["Run"]+'/03_Assembly/'+sample+'/assembly.fasta '\
                +options["Threads"])
            if not my_file.is_file():
                errors.append("[ERROR] STEP 11: Prokka annotation failed")
                error_count +=1
        else:
            print("Results already exist for "+sample)
    print("Done")
#ERROR DISPLAY----------------------------------------------------------------------------------------------
if error_count > 0:
    print("[ERROR] Assembly failed, see message(s) below to find out where:")
    for error in errors:
        print(error)
#===========================================================================================================

#TIMER END==================================================================================================
end = datetime.datetime.now()
timer = end - start
#CONVERT TO HUMAN READABLE----------------------------------------------------------------------------------
print("Analysis took: {} (H:MM:SS) \n".format(timer))
#===========================================================================================================
