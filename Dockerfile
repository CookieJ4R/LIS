FROM python:3.11.3-slim

WORKDIR /lis
COPY . .
RUN apt-get update && apt-get install -y gcc alsa-utils
RUN pip3 install -r requirements.txt
ENV PYTHONBUFFERED 1
ENV PYTHONPATH /lis/src

CMD ["/bin/bash"]

