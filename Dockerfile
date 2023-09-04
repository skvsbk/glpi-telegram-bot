FROM python:3.9-slim AS bot

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

# Env vars
#ENV TELEGRAM_TOKEN ${TELEGRAM_TOKEN}

RUN apt-get update
RUN apt-get install -y python3 python3-pip build-essential python3-venv
# python-dev

RUN mkdir -p /codebase /storage
ADD . /app
WORKDIR /app

RUN pip3 install -r requirements.txt
#RUN chmod +x /codebase/main.py

CMD python3 /app/main.py;