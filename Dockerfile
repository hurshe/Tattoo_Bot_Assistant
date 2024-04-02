# Dockerfile for building a Python-based Telegram bot
#
# This Dockerfile sets up an environment for running a Telegram bot
# written in Python. It installs the necessary dependencies specified
# in the requirements.txt file, copies the bot code into the container,
# and sets the entry point to run the main.py file.
#
# To use this Dockerfile, ensure your bot code is present in the same
# directory as this Dockerfile. Build the image using:
#
#   docker build -t my-telegram-bot .
#
# Then, run a container using:
#
#   docker run my-telegram-bot
#
# Author: Robert Khurshudian
# Version: 1.0
# Last updated: 2024-04-03

FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]