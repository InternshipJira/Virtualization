FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .
RUN apk add --no-cache build-base libffi-dev openssh-client git && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-base libffi-dev && \
    mkdir templates



RUN rm -rf ./local/lib/python3.9/site-packages/pip*
RUN rm -rf ./local/lib/python3.9/site-packages/setuptools*



COPY sftp_log_reader.py .
COPY key_exchange.sh .
COPY app.py .
COPY init_table.py .
COPY log_fetcher.py .
COPY templates/ /app/templates/
COPY start.sh .
    