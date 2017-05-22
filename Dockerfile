FROM ubuntu:16.04
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get -y install software-properties-common apt-transport-https
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN add-apt-repository 'deb [arch=amd64,i386] https://cran.rstudio.com/bin/linux/ubuntu xenial/'
RUN apt-get update
RUN apt-get install r-base python3 python3-pip -y
ADD requirements.txt .
RUN pip3 install -r requirements.txt
RUN mkdir /workbench
WORKDIR /workbench