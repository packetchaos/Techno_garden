FROM ubuntu

RUN apt-get update
RUN apt-get install -y python3-pip
RUN export DEBIAN_FRONTEND=noninteractive
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN ln -fs /usr/share/zoneinfo/America/Phoenix /etc/localtime

RUN pip3 install flask && pip3 install requests && pip3 install matplotlib
RUN echo 192.168.128.2 > /etc/resolv.conf

CMD mkdir /usr/src/app
CMD mkdir /usr/src/app/templates

ADD water_display.py /usr/src/app/
ADD templates/data.html /usr/src/app/templates/
ENV PATH "$PATH:/usr/bin/env/"

EXPOSE 5005

WORKDIR /app

CMD python3 /usr/src/app/water_display.py
