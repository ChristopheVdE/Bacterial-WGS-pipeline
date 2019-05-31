###################################################################################
#NAME SCRIPT: 01_demultiplex_compare.py
#AUTHOR: Christophe Van den Eynde  
#FUNCTION: Create a summary table displaying the ammount of reads found for each
#barcode, for each demultiplexer or demultiplexer combination used
#USAGE: ./01_demultiplex_compare.py ${demultiplex results folder}
###################################################################################

#TAKE INPUT FROM COMMAND LINE======================================================
import sys
path = sys.argv[1]
print("Making summary table of demultiplexing results found in: {}".format(path))
#==================================================================================

#PARSE RESULTS=====================================================================
import os
import gzip
summary = {}
for folder in os.listdir(path):
#GUPPY RESULTS---------------------------------------------------------------------
    if folder == "01_guppy":
        g_path = path+"/"+folder
        g_reads = 0
        for line in open(g_path+"/barcoding_summary.txt", "r"):
            # skip header line
            if g_reads >0:
                # extract barcode from line
                info = line.split("\t")
                barcode = info[1].replace("barcode", "BC")
                # add barcode as key if not yet present in dictionairy
                if barcode not in summary.keys():
                    summary[barcode] = [0,0,0,0]
                    # summary[barcode] = [0,1,2,3] 
                    # --> 0 = raw count of guppy reads for the barcode
                    # --> 1 = percentage of reads for a barcode (guppy)
                    # --> 2 = raw count of guppy_porechop reads for the barcode 
                    # --> 3 = percentage of reads for a barcode (guppy_porechop)
                # count barcode occurence
                summary[barcode][0] +=1
            g_reads +=1
#GUPPY + PORECHOP RESULTS----------------------------------------------------------
    elif folder == "02_guppy+porechop":
        gp_path = path + "/" + folder
        gp_reads = 0 
        for fastq in os.listdir(gp_path):
            if ".fastq.gz" in fastq:
                barcode = fastq.replace("none", "unclassified").replace(".fastq.gz","")
                # add barcode as key if not yet present in dictionairy
                if barcode not in summary.keys():
                    summary[barcode] = [0,0,0,0]
                for line in gzip.open(gp_path+"/"+fastq, "rt"):
                    # check for "barcode=" in line --> is sequence identifier line. 
                    # The @ is somethime also used in the scoring which could make parsing difficult
                    if "barcode=" in line:
                        summary[barcode][2] +=1
                        gp_reads +=1
#CALCULATE PERCENTAGES-------------------------------------------------------------
for barcode in summary.keys():
    summary[barcode][1] = int((summary[barcode][0] / (g_reads-1))*100)
    summary[barcode][3] = int((summary[barcode][2] / (gp_reads))*100)
#==================================================================================

#WRITE RESULTS TO FILE=============================================================
result = open(path + "/demultiplex_summary.txt","w")
result.write("{:15s} || {:10s} | {:3s} || {:16s} | {:3s}\n".format("Barcode","Guppy", "%","Guppy + Porechop", "%"))
result.write("-"*61 + "\n")
for key, value in sorted(summary.items()):
    result.write("{:15s} || {:10d} | {:3d} || {:16d} | {:3d}\n".format(key, value[0], value[1], value[2], value[3]))
result.write("-"*61 + "\n")
result.write("{:15s} || {:10d} | {:3d} || {:16d} | {:3d}\n".format("TOTAL READS", g_reads-1, 100, gp_reads, 100))
#==================================================================================

#PRINT RESULTS===================================================================
print("\n{:15s} || {:10s} | {:3s} || {:16s} | {:3s}".format("Barcode","Guppy", "%","Guppy + Porechop", "%"))
print("-"*61)
for key, value in sorted(summary.items()):
    print("{:15s} || {:10d} | {:3d} || {:16d} | {:3d}".format(key, value[0], value[1], value[2], value[3]))
print("-"*61)
print("{:15s} || {:10d} | {:3d} || {:16d} | {:3d}\n".format("TOTAL READS", g_reads-1, 100, gp_reads, 100))
#==================================================================================