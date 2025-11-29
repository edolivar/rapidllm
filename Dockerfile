FROM python:3.10-slim

WORKDIR /usr/local/transcribe

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update && apt install -y ffmpeg

EXPOSE 8000

RUN useradd -m dev
USER dev

