FROM python:3.9-alpine3.14

RUN apk --no-cache add nftables

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY daemon.py /daemon.py
ENTRYPOINT ["/daemon.py"]
