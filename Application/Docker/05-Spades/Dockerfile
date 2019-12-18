############################################################################################################
#NAME DOCKER IMAGE: christophevde/spades
#AUTHOR: Christophe Van den Eynde
#RUNNING: TRIMMOMATIC
#USAGE: $docker run -it christophevde/spades
############################################################################################################

# use official ubuntu runtime as parent image
FROM ubuntu:18.04

# download and install python
RUN  apt-get update \
  && apt-get install -y wget \
  && apt-get install -y python \
  && apt-get install -y dos2unix \
  && rm -rf /var/lib/apt/lists/*

# download and install SPAdes
RUN wget http://cab.spbu.ru/files/release3.13.1/SPAdes-3.13.1-Linux.tar.gz
RUN tar -xzf SPAdes-3.13.1-Linux.tar.gz
RUN cd SPAdes-3.13.1-Linux/bin/

#check versions of installed packages
RUN python --version

# add the Spades-script to the container
    ADD ./03_spades.sh /home/Scripts/03_spades.sh
    # Usage: "ADD 'location of file/folder on host' 'file/folder destination in container' "
# fix execute rights if necessairy
    RUN chmod 755 /home/Scripts/03_spades.sh
# fix wrong end of lines (when comming from windows) if necessairy
    RUN dos2unix /home/Scripts/03_spades.sh


