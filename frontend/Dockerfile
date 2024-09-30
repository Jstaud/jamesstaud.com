# frontend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Ensure /tmp directory exists
RUN mkdir -p /tmp

COPY /frontend .

RUN pip install --no-cache-dir -r requirements.txt

# Install Bitwarden Secrets Manager CLI (bws)
RUN apt-get update && apt-get install -y curl jq unzip \
    && curl -Lso /tmp/bws.zip https://github.com/bitwarden/cli/releases/download/v1.17.0/bws-linux-1.17.0.zip \
    && unzip /tmp/bws.zip -d /usr/local/bin \
    && chmod +x /usr/local/bin/bws

# Authenticate and retrieve secrets
RUN export BW_SESSION=$(bws login --raw) \
    && bws get secrets --project-id 1a7f001e-bd4f-450e-81dd-b1f800327bc7 --format json | jq -r '.[] | "export \(.key)=\(.value)"' > /app/secrets.sh \
    && . /app/secrets.sh

COPY . .

ENV PORT 8080
ENV BACKEND_API_URL=http://backend.jamesstaud.com/

EXPOSE 8080

CMD ["python", "app.py"]