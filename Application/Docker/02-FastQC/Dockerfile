############################################################################################################
#NAME DOCKER IMAGE: christophevde/fastqc
#AUTHOR: Christophe Van den Eynde
#RUNNING: TRIMMOMATIC
#USAGE: $docker run -it christophevde/fastqc:stable
############################################################################################################


# use official ubuntu runtime with openjdk10.0.2 as parent image
FROM adoptopenjdk/openjdk10:jdk-10.0.2.13

# download and install wget
RUN  apt-get update \
  && apt-get install -y wget \
  && apt-get install -y zip \
  && apt-get install -y perl \
  && apt-get install -y libfontconfig1 \
  && apt-get install -y dos2unix \
  && rm -rf /var/lib/apt/lists/*

# download and install fastqc
ENV URL=https://www.bioinformatics.babraham.ac.uk/projects/fastqc/
ENV ZIP=fastqc_v0.11.8.zip
ENV DST=/home

RUN wget $URL/$ZIP -O $DST/$ZIP
RUN unzip - $DST/$ZIP -d $DST
RUN rm $DST/$ZIP
RUN chmod 755 $DST/FastQC/fastqc
RUN ln -s $DST/FastQC/fastqc /usr/local/bin/fastqc

ENV PATH /usr/local/bin:$PATH

# the raw-data-folder of the host can also be added to the container like this --> but the folder location will be static
    # specify the raw-data-folder in the "$docker run ..." command to make the location dynamic

# add the FastQC-scripts (pre and post-trimming) to the container
    ADD ./QC01_fastqcRawData.sh /home/Scripts/QC01_fastqcRawData.sh
    ADD ./QC02_fastqcTrimmomatic.sh /home/Scripts/QC02_fastqcTrimmomatic.sh
    # Usage: "ADD 'location of file/folder on host' 'file/folder destination in container' "
        #abolsute paths required

# fix execute rights if necessairy
    RUN chmod 755 /home/Scripts/QC01_fastqcRawData.sh
    RUN chmod 755 /home/Scripts/QC02_fastqcTrimmomatic.sh
# fix wrong end of lines (when comming from windows) if necessairy
    RUN dos2unix /home/Scripts/QC01_fastqcRawData.sh
    RUN dos2unix /home/Scripts/QC02_fastqcTrimmomatic.sh

