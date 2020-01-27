#docker build -t g2p ./
#docker run -p 80:80 -p 443:443 g2p

FROM ubuntu

RUN apt-get update
#python version 2.7
RUN apt-get install apache2 php libapache2-mod-php python-pip unzip wget git chromium-browser -y
RUN pip install selenium

RUN git clone https://github.com/xbonner13/geno2pheno /var/www/html/

#if chromedriver does not work, get updated version
RUN cd /var/www/html && \
    wget https://chromedriver.storage.googleapis.com/79.0.3945.36/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    rm chromedriver_linux64.zip index.html

RUN chmod a+rw /var/www/html/
RUN chmod a+x /var/www/html/chromedriver

EXPOSE 80 443

CMD ["apachectl", "-D", "FOREGROUND"]