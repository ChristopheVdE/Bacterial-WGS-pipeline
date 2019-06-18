###########################################################################################################
#NAME SCRIPT: 01_Unicycler.py
#AUTHOR: Christophe Van den Eynde  
#Hybrid assembly
#USAGE: 'python3 01_Unicycler.py' (Linux) or 'python.exe 01_Unicycler.py' (Windows)
###########################################################################################################

#Import packages===========================================================================================
import os
import sys
from pathlib import Path
#==========================================================================================================

#TAKE INPUT FROM COMMAND LINE==============================================================================
Illumina = sys.argv[1]
MinIon = sys.argv[2]
Results = sys.argv[3]
cor_samples = sys.argv[4]
start_genes = sys.argv[5]
Threads = sys.argv[6]
#==========================================================================================================

#READ CORRESPONDING_SAMPLES.TXT============================================================================
print("Collecting data of corresponding Illumina and MinIon samples")
file = open(cor_samples, "r")
c = 0
samples = {}
for line in file:
    if c >= 1:
        #skip header line
        ids = line.replace('\n','').split(",")
        samples[ids[0]] = ids[1]
    c +=1
file.close()
#==========================================================================================================

#RUN UNICYCLER=============================================================================================
# unicycler -1 short_reads_1.fastq.gz -2 short_reads_2.fastq.gz -l long_reads.fastq.gz -o output_dir
for key, value in samples.items():
    my_file = Path(Results+'/'+value+"/assembly.fasta")
    if not my_file.is_file():
        print("Creating hybrid assembly with Illumina sample: "+value+" and MinIon sample with Barcode: "+key)
        os.system("unicycler \
            -1 "+Illumina+"/"+value+"/02_Trimmomatic/"+value+"_L001_R1_001_P.fastq.gz \
            -2 "+Illumina+"/"+value+"/02_Trimmomatic/"+value+"_L001_R2_001_P.fastq.gz \
            -l "+MinIon+"/BC"+key+".fastq.gz \
            -o "+Results+"/"+value+" \
            -t "+Threads+" \
            --no_correct \
            --start_genes "+start_genes+" \
            2>&1 | tee -a "+Results)
    else:
        print("Results for "+value+" already exist, nothing to be done")
#==========================================================================================================