############################################################################################################
#NAME DOCKER IMAGE: christophevde/multiqc
#AUTHOR: Christophe Van den Eynde
#RUNNING: MULTIQC
#USAGE: $docker run -it christophevde/multiqc
############################################################################################################

# use official ubuntu runtime as parent image
FROM ubuntu:18.04

# download and install python
RUN  apt-get update \
  && apt-get install -y python \
  && apt-get install -y python-pip \
  && apt-get install -y dos2unix \
  && rm -rf /var/lib/apt/lists/*

# download and install MultiQC
RUN pip install multiqc

#check versions of installed packages
RUN python --version
RUN pip --version

# add the FastQC-scripts (pre and post-trimming) to the container
    ADD ./QC01_multiqc_raw.sh /home/Scripts/QC01_multiqc_raw.sh 
    ADD ./QC02_multiqcTrimmomatic.sh /home/Scripts/QC02_multiqcTrimmomatic.sh
    # Usage: "ADD 'location of file/folder on host' 'file/folder destination in container' "
# fix execute rights if necessairy
    RUN chmod 755 /home/Scripts/QC01_multiqc_raw.sh 
    RUN chmod 755 /home/Scripts/QC02_multiqcTrimmomatic.sh
# fix wrong end of lines (when comming from windows) if necessairy
    RUN dos2unix /home/Scripts/QC01_multiqc_raw.sh 
    RUN dos2unix /home/Scripts/QC02_multiqcTrimmomatic.sh

