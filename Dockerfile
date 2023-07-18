# Use Python 3.10
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the project files to the working directory
COPY . /app

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
