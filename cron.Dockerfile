# Use Python 3.10
FROM python:3.10-slim

RUN apt-get update && apt-get install -y cron

# Set the working directory inside the container
WORKDIR /app

# Copy the project files to the working directory
COPY . /app

# Create folder for cron.log
RUN touch /var/log/cron.log
RUN chmod 777 /var/log/cron.log

# Copy cron file
COPY cronjob /etc/cron.d/cronjob

# Access
RUN chmod 0644 /etc/cron.d/cronjob

# Setup cron
RUN crontab /etc/cron.d/cronjob

# Start cron
CMD cron && tail -f /var/log/cron.log
