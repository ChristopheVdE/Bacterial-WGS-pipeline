############################################################################################################
# NAME: hybrid assembly.py
# AUTHOR: Christophe Van den Eynde
# FUNCTION: creates some texts files containing location variables that are used by the snakefile as input
# USAGE LINUX/MAC: python3 hybrid_assembly.py
# USAGE WINDOWS: python.exe hybrid_assembly.py
############################################################################################################

# IMPORT PACKAGES===========================================================================================
import os
import platform
import subprocess
import string
from datetime import date, datetime
from pathlib import Path
import shutil
import sys
# ==========================================================================================================

# CLASSES ==================================================================================================
# System Info ----------------------------------------------------------------------------------------------
class SystemInfo:
    def __init__(self):
        # SystemType: What System is the host running: Windows, MacOS, Unix (Darwin = MacOS)
        # SytemThreads: total amount of threads available to the system
        # Dockerthreads: total amount of threads availble to docker (dependend on docker-settings or the settings of the VM running docker)
        if "Windows" in platform.system():
            self.SystemType     = platform.system()
            self.SystemThreads  = subprocess.Popen('WMIC CPU Get NumberOfLogicalProcessors', shell=True, stdout=subprocess.PIPE)
        elif "Darwin" in platform.system():
            self.SystemType     = platform.system()
            self.SystemThreads  = subprocess.Popen('sysctl -n hw.ncpu', shell=True, stdout=subprocess.PIPE)
        else:
            self.SystemType     = "Unix"
            self.SystemThreads  = subprocess.Popen('nproc --all', shell=True, stdout=subprocess.PIPE)
        self.DockerThreads  = subprocess.Popen('docker run -it --rm --name ubuntu_bash christophevde/ubuntu_bash:v2.0_stable nproc --all', shell=True, stdout=subprocess.PIPE)

    def TranslateSubprocesOutput(self):
        # Translates the output of the "Threads"-related subprocesses to something useable
        for key, value in self.__dict__.items():
            if key in ["SystemThreads", "DockerThreads"]:
                for line in value.stdout:
                    if any(char.isdigit() for char in line.decode("UTF-8")):
                        self.__dict__[key] = int(line.decode("UTF-8"))

    def GetThreadsToUse(self):
        # Tip to increase maximum aoount of threads for Docker
        if self.DockerThreads < self.SystemThreads:
            print("You might still be able to increase the amount of threads available to Docker. Check your Docker or Virtual-Machine Settings")
        # Ask user for the amount of threads to use for the analysis
        self.UseThreads = int(input("How many threads do you want to use for the analysis (min = 1, max = {}): ".format(self.DockerThreads)))
        while self.UseThreads not in range(1, self.DockerThreads + 1):
            self.UseThreads = int(input("[ERROR] Chosen amount of threads is outside the possible range (min = 1, max = {}): ".format(self.DockerThreads)))

# User settings --------------------------------------------------------------------------------------------
class Settings:
    def __init__(self):
        self.Illumina               = input("location of Illumina samples: ")
        self.MinIon                 = input("location of Minion samples: ")
        self.CorrespondingSamples   = input("Input location of text file containing info on wich Illumina sample corresponds with which MinIon sample: ")
        self.Adaptors               = input("location of the adaptorfile for trimming: ")
        self.BarcodeKit             = input("which barcode-kit was used for the Minion samples: ")
        self.Results                = input("Where do you want to save the results: ")
        self.Run                    = date.today().strftime("%Y%m%d")
        self.Scripts                = os.path.dirname(os.path.realpath(__file__))

    def CheckLocations(self):
        for key in self.__dict__.keys():
            # locations that should be a directory
            if key in ["Illumina", "MinIon", "Scripts", "Results"]:
                while not os.path.isdir(self.__dict__[key]):
                    self.__dict__[key] = input("[ERROR] Directory not found, please provide correct location of {}: ".format(key))
            # locations that should be a file
            elif key in ["Adaptors"]:
                while not os.path.isfile(self.__dict__[key]):
                    self.__dict__[key] = input("[ERROR] File not found, please provide correct location of {}: ".format(key))

    def CreateFoldersIfNotExist(self):
        folders = [self.Results+"/Hybrid/"+self.Run,]
        for i in folders:
            os.makedirs(i, exist_ok=True)

    def CreateSettingsFile(self):
        file = open(os.path.dirname(os.path.realpath(__file__)) + "\\Modules\\Settings\\UserSettings" + self.Run + ".py", "w")
        for key, value in self.__dict__.items():
            file.write("{} = '{}'\n".format(key, value))
        file.close()

# Organism specific settings -------------------------------------------------------------------------------
class OrganismData:
    def __init__(self):
        self.Genus   = input("Genus of sample-organism: ")
        self.Species = input("Species of sample-organism: ")
        self.Kingdom = input("Kingdom of sample-organism: ")
        self.StartGenes = input("Location of multifasta containing start-genes for annotation: ")

    def CheckLocations(self):
        for key in self.__dict__.keys():
            # locations that should be a file
            if key == "StartGenes":
                while not os.path.isfile(self.__dict__[key]):
                    self.__dict__[key] = input("[ERROR] File not found, please provide correct location of {}: ".format(key))

    def CreateOrganismFile(self):
        file = open(os.path.dirname(os.path.realpath(__file__)) + "\\Modules\\OrganismData\\" + self.Species + ".py", "w")
        for key, value in self.__dict__.items():
            file.write("{} = '{}'\n".format(key, value))
        file.close()

# Converst Windows folder paths for mountig in Docker ------------------------------------------------------
class PathConverter:
    def __init__(self, SystemType, class1, class2):
        if SystemType == 'Windows':
            for data in [class1, class2]:
                for key, value in data.__dict__.items():
                    for letter in list(string.ascii_lowercase+string.ascii_uppercase):
                        if value.startswith(letter+":/"):
                            self.__dict__[key] = value.replace(letter+":/","/"+letter.lower()+"//").replace('\\','/')
                        elif value.startswith(letter+":\\"):
                            self.__dict__[key] = value.replace(letter+":\\","/"+letter.lower()+"//").replace('\\','/')
        else:
            for key, value in data.__dict__.items():
                self.__dict__[key] = value

# Timer ----------------------------------------------------------------------------------------------------
class Timer:
    def __init__(self):
        self.AnalysisTime = datetime.now()

    def NewTimer(self, step):
        self.__dict__[step] = datetime.now()

    def StopTimer(self, step):
        self.__dict__[step] = datetime.now() - self.__dict__[step]
        self.__dict__[step] = str(self.__dict__[step]).split(":")
        self.__dict__[step] = "{}H, {}MM, {}SS".format(self.__dict__[step][0], self.__dict__[step][1], self.__dict__[step][2].split(".")[0])

# FUNCTIONS==================================================================================================
# SHORT READ SAMPLE LIST CREATION----------------------------------------------------------------------------
def sample_list(Illumina):
    global ids
    ids =[]
    for sample in os.listdir(Illumina):
        if ".fastq.gz" in sample:
            ids.append(sample.replace('_L001_R1_001.fastq.gz','').replace('_L001_R2_001.fastq.gz',''))
    ids = sorted(set(ids))
    return ids
# ===========================================================================================================

# ASSEMBLY PREPARATION: USER INPUT===========================================================================
# Get sytem info --------------------------------------------------------------------------------------------
system = SystemInfo()
system.TranslateSubprocesOutput()
system.GetThreadsToUse()

# Get general settings --------------------------------------------------------------------------------------
UserSettings = Settings()
UserSettings.CheckLocations()
UserSettings.CreateFoldersIfNotExist()

# Get organism specific info --------------------------------------------------------------------------------
Organism = OrganismData()
Organism.CheckLocations()

# Convert folderpaths for mounting in docker-container when using Windows -----------------------------------
ConvertedPaths = PathConverter(system.SystemType, UserSettings, Organism)

# Save the info in the corresponding file -------------------------------------------------------------------
UserSettings.CreateSettingsFile()
Organism.CreateOrganismFile()

# Activate Timer: Full analysis -----------------------------------------------------------------------------
timer = Timer()

# Enable error collection -----------------------------------------------------------------------------------
errors = []
error_count = 0
# ===========================================================================================================

# ASSEMBLY PREPARATION: GENERAL PREPARATION =================================================================
# Move and rename required "info"-files to "Results"-folder -------------------------------------------------
shutil.copy(UserSettings.CorrespondingSamples, UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/corresponding_samples.txt")
if not Organism.StartGenes == '':
    shutil.copy(Organism.StartGenes, UserSettings.Results + "/Hybrid/" + UserSettings.Run + "/start_genes.fasta")

# List content of "Illumina"-folder and save it in a file ---------------------------------------------------
file = open(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/sampleList.txt",mode="w")
for i in sample_list(UserSettings.Illumina):
    file.write(i+"\n")
file.close()

# COPY ILLUMINA SAMPLES TO RESULTS---------------------------------------------------------------------------
print("\n[HYBRID][SHORT READS] Copying rawdata") 
copy = 'docker run -it --rm \
    --name copy_rawdata \
    -v "'+ConvertedPaths.Illumina+':/home/rawdata/" \
    -v "'+ConvertedPaths.Results+':/home/Pipeline/" \
    -v "'+ConvertedPaths.Scripts+':/home/Scripts/" \
    christophevde/ubuntu_bash:v2.2_stable \
    /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/01_copy_rawdata.sh \
    && sh /home/Scripts/Hybrid/Short_read/01_copy_rawdata.sh '+UserSettings.Run+'"'
os.system(copy)
print("Done")

# ============================================================================================================


while error_count == 0:
# [HYBRID ASSEMBLY] SHORT READS ==============================================================================

# SHORT READS: FASTQC RAWDATA (DOCKER)-------------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] FastQC rawdata")
    for sample in ids:
        my_file1 = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/01_Short_reads/"+sample+"/01_QC-Rawdata/QC_FastQC/"+sample+"_L001_R1_001_fastqc.html")
        my_file2 = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/01_Short_reads/"+sample+"/01_QC-Rawdata/QC_FastQC/"+sample+"_L001_R1_001_fastqc.html")
        if not my_file1.is_file() and not my_file2.is_file():
            os.system('docker run -it --rm \
                --name fastqc_raw \
                -v "'+ConvertedPaths.Scripts+':/home/Scripts/" \
                -v "'+ConvertedPaths.Results+':/home/Pipeline/" \
                christophevde/fastqc:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC01_FastQC_Raw.sh \
                && /home/Scripts/Hybrid/Short_read/QC01_FastQC_Raw.sh '+sample+' '+UserSettings.Run+' '+system.UseThreads+'"')
            if not my_file1.is_file() or not my_file2.is_file():
                errors.append("[ERROR] STEP 1: FastQC; quality control rawdata (short reads)")
                error_count +=1
        else:
            print("  - FastQC results for the rawdata of sample "+sample+" already exists")
    print("Done")

#SHORT READS: MULTIQC RAWDATA (DOCKER)-----------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] MultiQC rawdata")
    #FULL RUN------------------------------------------------------------------------------------------------
    my_file = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/01_Short_reads/QC_MultiQC/QC-Rawdata/multiqc_report.html")
    if not my_file.is_file():
        #CREATE TEMP FOLDER----------------------------------------------------------------------------------
        os.makedirs(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/temp/", exist_ok=True)
        #COPY FASTQC RESULTS---------------------------------------------------------------------------------
        print("creating temporary directory to copy all fastqc results of rawdata")
        for sample in ids:
            os.system('docker run -it --rm\
                --name copy_fastqc\
                -v "'+UserSettings.Results+'/Hybrid/'+UserSettings.Run+'/01_Short_reads/'+sample+'/01_QC-Rawdata/QC_FastQC/:/home/fastqc" \
                -v "'+UserSettings.Results+'/Hybrid/'+UserSettings.Run+'/temp/:/home/multiqc" \
                christophevde/ubuntu_bash:v2.2_stable \
                /bin/bash -c "cp -rn /home/fastqc/* /home/multiqc"')
        #EXECUTE MULTIQC-------------------------------------------------------------------------------------
            os.system('docker run -it --rm \
                --name multiqc_raw \
                -v "'+ConvertedPaths.Scripts+':/home/Scripts/" \
                -v "'+ConvertedPaths.Results+':/home/Pipeline/" \
                christophevde/multiqc:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC01_MultiQC_Raw_FullRun.sh \
                && /home/Scripts/Hybrid/Short_read/QC01_MultiQC_Raw_FullRun.sh '+UserSettings.Run+'"')
            if not my_file.is_file():
                errors.append("[ERROR] STEP 2: MultiQC; quality control rawdata (short reads)")
                error_count +=1
        else:
            print("  - MultiQC results for the full run (rawdata) already exists")
        #REMOVE TEMP FOLDER----------------------------------------------------------------------------------
        os.system('docker run -it --rm\
            --name delete_temp_folder\
            -v "'+UserSettings.Results+'/Hybrid/'+UserSettings.Run+':/home/multiqc" \
            christophevde/ubuntu_bash:v2.2_stable \
            /bin/bash -c "rm -R /home/multiqc/temp"')
    #EACH SAMPLE SEPARALTY-----------------------------------------------------------------------------------
    for sample in ids:
        my_file = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/01_Short_reads/"+sample+"/01_QC-Rawdata/QC_MultiQC/multiqc_report.html")
        if not my_file.is_file():
            os.system('docker run -it --rm \
                --name multiqc_raw \
                -v "'+ConvertedPaths.Scripts+':/home/Scripts/" \
                -v "'+ConvertedPaths.Results+':/home/Pipeline/" \
                christophevde/multiqc:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC01_MultiQC_Raw_oneSample.sh \
                && /home/Scripts/Hybrid/Short_read/QC01_MultiQC_Raw_oneSample.sh '+sample+' '+UserSettings.Run+'"')
            if not my_file.is_file():
                errors.append("[ERROR] STEP 2: MultiQC; quality control rawdata (short reads)")
                error_count +=1
        else:
            print("  - MultiQC results for the rawdata of sample "+sample+" already exists")
    print("Done")
#SHORT READS: TRIMMING (DOCKER)------------------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] Trimming")
    for sample in ids:
        my_file1 = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/01_Short_reads/"+sample+"/02_Trimmomatic/"+sample+"_L001_R1_001_P.fastq.gz")
        my_file2 = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/01_Short_reads/"+sample+"/02_Trimmomatic/"+sample+"_L001_R2_001_P.fastq.gz")
        if not my_file1.is_file() and not my_file2.is_file():
            os.system('docker run -it --rm \
                --name trimmomatic \
                -v "'+ConvertedPaths.Scripts+':/home/Scripts/" \
                -v "'+ConvertedPaths.Results+':/home/Pipeline/" \
                christophevde/trimmomatic:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/02_runTrimmomatic.sh \
                && /home/Scripts/Hybrid/Short_read/02_runTrimmomatic.sh '+sample+' '+UserSettings.Run+' '+system.UseThreads+'"')
        if not my_file1.is_file() or not my_file2.is_file():
                errors.append("[ERROR] STEP 3: TRIMMOMATIC; trimming adaptors form reads (short reads)")
                error_count +=1
        else:
            print("  - Trimmomatic results of sample "+sample+" already exists")
    print("Done")
#SHORT READS: FASTQC TRIMMED (DOCKER)------------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] FastQC Trimmed data")
    for sample in ids:
        my_file1 = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/01_Short_reads/"+sample+"/03_QC-Trimmomatic_Paired/QC_FastQC/"+sample+"_L001_R1_001_P_fastqc.html")
        my_file2 = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/01_Short_reads/"+sample+"/03_QC-Trimmomatic_Paired/QC_FastQC/"+sample+"_L001_R1_001_P_fastqc.html")
        if not my_file1.is_file() and not my_file2.is_file():
            os.system('docker run -it --rm \
                --name fastqc_trim \
                -v "'+ConvertedPaths.Scripts+':/home/Scripts/" \
                -v "'+ConvertedPaths.Results+':/home/Pipeline/" \
                christophevde/fastqc:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC02_FastQC_Trim.sh \
                && /home/Scripts/Hybrid/Short_read/QC02_FastQC_Trim.sh '+sample+' '+UserSettings.Run+' '+system.UseThreads+'"')
            if not my_file1.is_file() or not my_file2.is_file():
                errors.append("[ERROR] STEP 4: FastQC; quality control trimmed data (short reads)")
                error_count +=1
        else:
            print("  - FastQC results for the trimmed data of sample "+sample+" already exists")
    print("Done")
#SHORT READS: MULTIQC TRIMMED (DOCKER)-----------------------------------------------------------------------
    print("\n[HYBRID][SHORT READS] MultiQC Trimmed data")
    #FULL RUN------------------------------------------------------------------------------------------------
    my_file = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/01_Short_reads/QC_MultiQC/QC-Trimmed/multiqc_report.html")
    if not my_file.is_file():
    #CREATE TEMP FOLDER--------------------------------------------------------------------------------------
        os.makedirs(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/temp/", exist_ok=True)
        #COPY FASTQC RESULTS---------------------------------------------------------------------------------
        print("creating temporary directory to copy all fastqc results of trimmed data")
        for sample in ids:
            os.system('docker run -it --rm \
                --name copy_fastqc\
                -v "'+UserSettings.Results+'/Hybrid/'+UserSettings.Run+'/01_Short_reads/'+sample+'/03_QC-Trimmomatic_Paired/QC_FastQC/:/home/fastqc" \
                -v "'+UserSettings.Results+'/Hybrid/'+UserSettings.Run+'/temp/:/home/multiqc" \
                christophevde/ubuntu_bash:v2.2_stable \
                /bin/bash -c "cp -rn /home/fastqc/* /home/multiqc"')
        #EXECUTE MULTIQC-------------------------------------------------------------------------------------
        os.system('docker run -it --rm \
            --name multiqc_trimmed \
            -v "'+ConvertedPaths.Scripts+':/home/Scripts/" \
            -v "'+ConvertedPaths.Results+':/home/Pipeline/" \
            christophevde/multiqc:v2.2_stable \
            /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC02_MultiQC_Trim_FullRun.sh \
            && /home/Scripts/Hybrid/Short_read/QC02_MultiQC_Trim_FullRun.sh '+UserSettings.Run+'"')
        if not my_file.is_file():
            errors.append("[ERROR] STEP 5: MultiQC; quality control trimmed data (short reads)")
            error_count +=1
        else:
            print("  - MultiQC results for the full run (trimmed data) already exists")
        #REMOVE TEMP FOLDER----------------------------------------------------------------------------------
        os.system('docker run -it --rm \
            --name delete_temp_folder\
            -v "'+UserSettings.Results+'/Hybrid/'+UserSettings.Run+':/home/multiqc" \
            christophevde/ubuntu_bash:v2.2_stable \
            /bin/bash -c "rm -R /home/multiqc/temp"')
    #EACH SAMPLE SEPARALTY-----------------------------------------------------------------------------------
    for sample in ids:
        my_file = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/01_Short_reads/"+sample+"/03_QC-Trimmomatic_Paired/QC_MultiQC/multiqc_report.html")
        if not my_file.is_file():
            os.system('docker run -it --rm \
                --name multiqc_raw \
                -v "'+ConvertedPaths.Scripts+':/home/Scripts/" \
                -v "'+ConvertedPaths.Results+':/home/Pipeline/" \
                christophevde/multiqc:v2.2_stable \
                /bin/bash -c "dos2unix -q /home/Scripts/Hybrid/Short_read/QC02_MultiQC_Trim_oneSample.sh \
                && /home/Scripts/Hybrid/Short_read/QC02_MultiQC_Trim_oneSample.sh '+sample+' '+UserSettings.Run+'"')
            if not my_file.is_file():
                errors.append("[ERROR] STEP 5: MultiQC; quality control rawdata (short reads)")
                error_count +=1
        else:
            print("  - MultiQC results for the trimmed data of sample "+sample+" already exists")
    print("Done")
# ===========================================================================================================


# [HYBRID ASSEMBLY] LONG READS ==============================================================================
#LONG READS: DEMULTIPLEXING (GUPPY)-------------------------------------------------------------------------
    print("\n[HYBRID][LONG READS] Guppy: demultiplexing")
    my_file = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/02_Long_reads/01_Demultiplex/barcoding_summary.txt")
    if not my_file.is_file():
        #file doesn't exist -> guppy demultiplex hasn't been run
        if system == "UNIX":
            os.system("dos2unix -q "+UserSettings.Scripts+"/Hybrid/Long_read/01_demultiplex.sh")
        os.system('sh ./Scripts/Hybrid/Long_read/01_demultiplex.sh '\
            +UserSettings.MinIon+'/fastq/pass '\
            +UserSettings.Results+' '\
            +UserSettings.Run+' '\
            +system.UseThreads)
        if not my_file.is_file():
            errors.append("[ERROR] STEP 6: Guppy demultiplexing failed")
            error_count +=1
    else:
        print("  - Results already exist")
    print("Done")
#LONG READS: QC (PYCOQC)------------------------------------------------------------------------------------
    print("\n[HYBRID][LONG READS] PycoQC: Performing QC on Long reads")
    if not os.path.exists(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/02_Long_reads/02_QC/"):
        os.makedirs(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/02_Long_reads/02_QC/")
    my_file = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/02_Long_reads/02_QC/QC_Long_reads.html")
    if not my_file.is_file():
        #file doesn't exist -> pycoqc hasn't been run
        if system == "UNIX":
            os.system("dos2unix -q "+UserSettings.Scripts+"/Hybrid/Long_read/02_pycoQC.sh") 
        os.system('sh ./Scripts/Hybrid/Long_read/02_pycoQC.sh '\
            +UserSettings.MinIon+'/fast5/pass '\
            +UserSettings.Results+'/Hybrid/'+UserSettings.Run+' '\
            +system.UseThreads)
        if not my_file.is_file():
            errors.append("[ERROR] STEP 7: PycoQC quality control failed")
            error_count +=1
    else:
        print("Results already exist")
    print("Done")
#LONG READS: DEMULTIPLEXING + TRIMMING (PORECHOP)-----------------------------------------------------------
    print("\n[HYBRID][LONG READS] Porechop: Trimming Long reads")
    my_file = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/02_Long_reads/02_QC/demultiplex_summary.txt")
    if not my_file.is_file():
        #file doesn't exist -> porechop trimming hasn't been run
        if system == "UNIX":
            os.system("dos2unix -q "+UserSettings.Scripts+"/Hybrid/Long_read/03_Trimming.sh")
        #demultiplex correct + trimming 
        os.system('sh '+UserSettings.Scripts+'/Hybrid/Long_read/03_Trimming.sh '\
            +UserSettings.Results+'/Hybrid/'+UserSettings.Run+'/02_Long_reads/01_Demultiplex '\
            +UserSettings.Results+' '\
            +UserSettings.Run+' '\
            +system.UseThreads)
        #creation of summary table of demultiplexig results (guppy and porechop)
        os.system("python3 "+UserSettings.Scripts+"/Hybrid/Long_read/04_demultiplex_compare.py "\
            +UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/02_Long_reads/01_Demultiplex/ "\
            +UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/02_Long_reads/03_Trimming/ "\
            +UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/02_Long_reads/02_QC/")
        if not my_file.is_file():
            errors.append("[ERROR] STEP 8: Porechop demuliplex correction and trimming failed")
            error_count +=1
    else:
        print("Results already exist")
    print("Done")
# ===========================================================================================================


# [HYBRID ASSEMBLY] HYBRID ASSEMBLY =========================================================================
    #READ SAMPLE FILE---------------------------------------------------------------------------------------
    print("Collecting data of corresponding Illumina and MinIon samples")
    file = open(UserSettings.Results+'/Hybrid/'+UserSettings.Run+'/corresponding_samples.txt', "r")
    c = 0
    samples = {}
    for line in file:
        if c >= 1:
            #skip header line
            ids = line.replace('\n','').split(",")
            samples[ids[0]] = ids[1]
        c +=1
    file.close()
    #EXECUTE UNICYCLER---------------------------------------------------------------------------------------
    print("\n[HYBRID][ASSEMBLY] Unicycler: building hybrid assembly")
    if system == "UNIX":
        os.system("dos2unix -q "+UserSettings.Scripts+"/Long_read/05_Unicycler.sh")
    for key, value in samples.items():
        #key = barcode; value = Illumina ID
        my_file = Path(UserSettings.Results+'/Hybrid/'+UserSettings.Run+'/03_Assembly/'+value+'/assembly.gfa')
        if not my_file.is_file():
            print("Creating hybrid assembly with Illumina sample: "+value+" and MinIon sample with Barcode: "+key)
            os.system('sh '+UserSettings.Scripts+'/Hybrid/01_Unicyler.sh'\
                +value+' '\
                +key+' '\
                +UserSettings.Results+'/Hybrid/'+UserSettings.Run+' '\
                +system.UseThreads)
            if not my_file.is_file():
                errors.append("[ERROR] STEP 9: Unicycler hybrid assembly failed")
                error_count +=1
        else:
            print("  - Results for sample "+value+" already exist")
        print("Done")
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
        os.system("dos2unix -q "+UserSettings.Scripts+"/Hybrid/02_Prokka.sh")
    for sample in os.listdir(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/03_Assembly/"):
        my_file = Path(UserSettings.Results+"/Hybrid/"+UserSettings.Run+"/04_Prokka/"+sample+"/*.gff")
        if not my_file.is_file():
            os.system('sh '+UserSettings.Scripts+'/Hybrid/02_Prokka.sh '\
                +UserSettings.Results+'/Hybrid/'+UserSettings.Run+'/04_Prokka/'+sample+' '\
                +Organism.Genus+' '\
                +Organism.Species+' '\
                +Organism.Kingdom+' '\
                +UserSettings.Results+'/Hybrid/'+UserSettings.Run+'/03_Assembly/'+sample+'/assembly.fasta '\
                +system.UseThreads)
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
timer.StopTimer("AnalysisTime")
#CONVERT TO HUMAN READABLE----------------------------------------------------------------------------------
print("Analysis took: {} (H:MM:SS) \n".format(timer))
#===========================================================================================================
