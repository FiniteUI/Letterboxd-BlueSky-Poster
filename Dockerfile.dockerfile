FROM python:3.13-slim

ENV DOCKER=1

WORKDIR "/app"

COPY ConfigurationFile.py .
COPY app.py .
COPY BlueSky.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "-u", "app.py"]