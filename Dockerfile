# Use Python 3.10
FROM python:3.10-slim

# Installing cron package
# RUN apt-get update && apt-get -y install cron

# Set the working directory inside the container
WORKDIR /app

# Copy the project files to the working directory
COPY . /app
COPY curators.json /app/curators.json
COPY playlists.json /app/playlists.json
COPY tracks.json /app/tracks.json
COPY processed.txt /app/processed.txt

# # Copy the crontab files and run_parse.sh
# COPY cronjob /etc/cron.d/cronjob

# Setting the execution rights
#RUN chmod 0644 /etc/cron.d/cronjob

# Adding a cronjob
# RUN crontab /etc/cron.d/cronjob

# Install Poetry
RUN pip3 install --no-cache-dir poetry

# Install project dependencies
RUN poetry install --no-root --no-dev

# Expose port 8000
EXPOSE 8000

# Set the environment variable
ENV PORT=8000

# Start the FastAPI server using uvicorn
CMD ["poetry", "run", "uvicorn", "belinda_app.app:app", "--host", "0.0.0.0", "--port", "8000"]
