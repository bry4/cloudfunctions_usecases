FROM python:3.10-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY service-account-key.json /app/service-account-key.json

ENV GOOGLE_APPLICATION_CREDENTIALS /app/service-account-key.json

COPY src/main.py .
#COPY src/schemas.json .

# Expose port 8080 in containet
EXPOSE 8080

# Starting local server
CMD ["functions-framework", "--target=main", "--host=0.0.0.0", "--port=8080"]
