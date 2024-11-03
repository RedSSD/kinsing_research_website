FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /code

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    git \
    wget\
    && rm -rf /var/lib/apt/lists/*

# Install project requirements
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV CHROME_VERSION=123.0.6312.122-1
RUN wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb
RUN apt-get -y update
RUN apt-get install -y ./google-chrome-stable_${CHROME_VERSION}_amd64.deb

# Copy project
COPY . /code/

# Expose port 8000 to allow communication to/from the container
EXPOSE 8000
