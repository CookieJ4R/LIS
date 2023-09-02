FROM python:3.11.3-slim

WORKDIR /lis
COPY . .
RUN pip3 install -r requirements.txt
ENV PYTHONBUFFERED 1
ENV PYTHONPATH /lis/src

CMD ["/bin/bash"]

