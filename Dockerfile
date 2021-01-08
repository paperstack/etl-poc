FROM python:3.7

# System prerequisites
RUN apt-get update \
 && apt-get -y install build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

ADD . /app

EXPOSE 8080

CMD prefect server start --postgres-port 5433
