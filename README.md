# Telegram Bot Docker Container

This repository contains a Telegram bot packaged in a Docker container. Below are the instructions on how to build the container locally or pull it from Docker Hub and run it with the necessary environment variables.

## Requirements
- Docker installed on your machine.
- A valid Telegram Bot Token (TG_TOKEN).

## How to Build and Run Locally

### 1. Build the Docker Image
First, you need to build the Docker image from the Dockerfile. Run the following command in the root directory of the project:

```bash
docker build -t telegram-bot .
```

###  2. Run the Docker Container
```bash
docker run -e TG_TOKEN=<your_token> telegram-bot
```


## How to Pull and Run from Docker Hub

### 1. Pull the Image
You can pull the latest image from Docker Hub by running:

```bash
docker pull ezzysoft/telegram-bot:latest
```

###  2. Run the Docker Container
```bash
docker run -e TG_TOKEN=<your_token> ezzysoft/telegram-bot:latest
```
