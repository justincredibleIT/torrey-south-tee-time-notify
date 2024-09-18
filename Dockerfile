# Use the official lightweight Python 3.9 image as the base
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /

# Update package lists, install Firefox and geckodriver, and clean up in one step
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    firefox-esr && \
    wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz && \
    tar -xvzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz && \
    apt-get remove --purge -y wget && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for configuration
ENV TEE_TIMES_USERNAME=""
ENV TEE_TIMES_PASSWORD=""
ENV EMAIL_FROM=""
ENV EMAIL_TO=""
ENV GMAIL_APP_PASSWORD=""
ENV ALERT_TIMES_WEEKDAY=""
ENV ALERT_TIMES_WEEKEND=""

# Set environment variable to indicate config file path
#ENV CONFIG_FILE_PATH=/config.yml

VOLUME /config

# Run get-tee-time.py when the container launches
CMD ["python", "get-tee-time.py"]
