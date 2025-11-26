FROM python:3.14.0-trixie

WORKDIR /usr/local/transcribe

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

RUN useradd dev
USER dev

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0"]
