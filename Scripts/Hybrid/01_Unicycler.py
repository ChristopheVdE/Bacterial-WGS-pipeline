###########################################################################################################
#NAME SCRIPT: 01_Unicycler.py
#AUTHOR: Christophe Van den Eynde  
#Hybrid assembly
#USAGE: 'python3 01_Unicycler.py' (Linux) or 'python.exe 01_Unicycler.py' (Windows)
###########################################################################################################

#TAKE INPUT FROM COMMAND LINE==============================================================================
import os
import sys
Illumina = sys.argv[1]
MinIon = sys.argv[2]
Results = sys.argv[3]
cor_samples = sys.argv[4]
#==========================================================================================================

#READ CORRESPONDING_SAMPLES.TXT============================================================================
print("Collecting data of corresponding Illumina and MinIon samples")
file = open(cor_samples)
c = 0
samples = {}
for line in samples:
    if c >= 1:
        #skip header line
        ids = line.split("\t")
        samples[ids[0]] = ids[1]
file.close()
#==========================================================================================================

#RUN UNICYCLER=============================================================================================
# unicycler \-1 short_reads_1.fastq.gz -2 short_reads_2.fastq.gz -l long_reads.fastq.gz -o output_dir
for key, value in samples.items():
    print("Creating hybrid assembly with Illumina sample: "+value+" and MinIon sample with Barcode: "+key)
    os.system("unicycler \
        -1 "+Illumina+"/"+value+"_L001_R1_001.fastq.gz.fastq.gz \
        -2 "+Illumina+"/"+value+"_L001_R2_001.fastq.gz.fastq.gz \
        -l "+MinIon+"/BC"+key+".fastq.gz \
        -o output_dir")
#==========================================================================================================