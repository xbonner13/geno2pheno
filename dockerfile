FROM python:3.10

WORKDIR /app

RUN pip install selenium==4.28.0

EXPOSE 8080

CMD sleep infinity