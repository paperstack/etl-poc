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

CMD prefect agent local start --api https://api.prefect.io --token Go-8i0PtDRX-PYH24Gz92Q --agent-address http://localhost:8080 --name aptible-dev  --label st_lukes