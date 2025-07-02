FROM python:3.11-slim

ENV DOCKER_ENV=1

# Install Chromium and ChromiumDriver (compatible with ARM)
RUN apt-get update && apt-get install -y \
    chromium chromium-driver wget unzip curl gnupg fonts-liberation \
    libglib2.0-0 libnss3 libxss1 libasound2 libgtk-3-0 libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install selenium biopython

# Set Chromium binary path for Selenium
ENV CHROME_BIN=/usr/bin/chromium

WORKDIR /app

CMD sleep infinity