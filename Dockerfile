FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    cron \
    mpg123 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/


CMD ["sh", "-c", "python setup.py && cron && tail -f /dev/null"]