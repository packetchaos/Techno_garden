FROM ubuntu

RUN apt-get update
RUN apt-get install -y python3-pip
RUN pip3 install flask && pip3 install requests

CMD mkdir /usr/src/app
CMD mkdir /usr/src/app/templates

ADD water_data_capture.py /usr/src/app/
ADD database.py /usr/src/app/
ADD templates/water.html /usr/src/app/templates/
ADD templates/success.html /usr/src/app/templates/
ENV PATH "$PATH:/usr/bin/env/"

EXPOSE 5004

WORKDIR /app

CMD python3 /usr/src/app/water_data_capture.py
