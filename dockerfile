#docker build -t g2p ./
#docker run -p 80:80 -p 443:443 g2p

FROM ubuntu

RUN apt-get update
RUN apt-get install apache2 python-pip unzip wget git chromium-browser -y
RUN pip install selenium

#if chromedriver does not work, get updated version

RUN git clone https://github.com/xbonner13/geno2pheno /var/www/html/

RUN cd /var/www/html && \
    rm chromedriver index.html && \
    wget https://chromedriver.storage.googleapis.com/79.0.3945.36/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    rm chromedriver_linux64.zip

RUN chmod a+rw /var/www/html/
RUN chmod a+x /var/www/html/chromedriver

EXPOSE 80 443

CMD ["apachectl", "-D", "FOREGROUND"]