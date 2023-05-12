FROM python:3.10-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY service-account-key.json /app/service-account-key.json

ENV GOOGLE_APPLICATION_CREDENTIALS /app/service-account-key.json

COPY src/main.py .
COPY src/files_mapping.json .
COPY src/schemas.json .

# Starting local server
CMD ["python", "main.py"]
