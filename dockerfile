FROM python:3.8

MAINTAINER Michael Clark <clarkmu@unc.edu>

ENV PORT=8080

LABEL maintainer="Michael Clark <clarkmu@unc.edu>" \
    io.k8s.description="Create an API version of Geno2Pheno" \
    io.k8s.display-name="Geno2Pheno Server" \
    io.openshift.expose-services="${PORT}:https"

# update Ubuntu
RUN apt update && apt upgrade -y

RUN apt install software-properties-common wget vim unzip -y

RUN cd /root && \
    wget https://chromedriver.storage.googleapis.com/79.0.3945.36/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip

# install a webserver
RUN pip3 install fastapi starlette uvicorn python-multipart uuid

EXPOSE $PORT

WORKDIR /app

COPY . .
RUN chmod -R 777 /app
RUN chmod -R 777 /root
USER 1001

CMD uvicorn server:app --reload --host 0.0.0.0 --port $PORT
# CMD sleep infinity