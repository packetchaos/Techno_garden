FROM ubuntu

RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install flask && pip3 install requests

CMD mkdir /usr/src/app
CMD mkdir /usr/src/app/templates

ADD water_display.py /usr/src/app/
ADD templates/data.html /usr/src/app/templates/
ENV PATH "$PATH:/usr/bin/env/"

EXPOSE 5005

WORKDIR /app

CMD python3 /usr/src/app/water_display.py
