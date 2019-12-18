############################################################################################################
#NAME DOCKER IMAGE: christophevde/trimmomatic
#AUTHOR: Christophe Van den Eynde
#RUNNING: TRIMMOMATIC
#USAGE: $docker run -it christophevde/trimmomatic
############################################################################################################

# use official ubuntu runtime with openjdk10.0.2 as parent imag
FROM adoptopenjdk/openjdk10:jdk-10.0.2.13

# download and install wget
RUN  apt-get update \
  && apt-get install -y wget \
  && apt-get install -y zip \
  && apt-get install -y dos2unix \
  && rm -rf /var/lib/apt/lists/*

# download and install fastqc
ENV URL=http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/
ENV ZIP=Trimmomatic-0.39.zip
ENV DST=/home

RUN wget $URL/$ZIP -O $DST/$ZIP
RUN unzip - $DST/$ZIP -d $DST
RUN rm $DST/$ZIP
RUN chmod 755 $DST/Trimmomatic-0.39/trimmomatic-0.39.jar
RUN ln -s $DST/Trimmomatic-0.39/trimmomatic-0.39.jar /usr/local/bin/trimmomatic-0.39.jar

ENV PATH /usr/local/bin:$PATH

# the raw-data-folder of the host can also be added to the container like this --> but the folder location will be static
    # specify the raw-data-folder in the "$docker run ..." command to make the location dynamic
    
# add the Trimmomatic-script to the container
    ADD ./02_runTrimmomatic.sh /home/Scripts/02_runTrimmomatic.sh
# fix execute rights if necessairy
    RUN chmod 755 /home/Scripts/02_runTrimmomatic.sh
# fix wrong end of lines (when comming from windows) if necessairy
    RUN dos2unix /home/Scripts/02_runTrimmomatic.sh

# add the adaptor file to the container
ADD ./NexteraPE-PE.fa /home/adapters/NexteraPE-PE.fa
    # Usage: "ADD 'location of file/folder on host' 'file/folder destination in container' "

