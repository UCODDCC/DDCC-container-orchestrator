FROM alpine:latest
RUN apk --no-cache add python3 docker openrc
RUN rc-update add docker default
RUN pip3 install --upgrade pip setuptools
ADD . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN ls
CMD python3 -u app.py
