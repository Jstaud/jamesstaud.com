# backend/Dockerfile
FROM python:3.9-slim
WORKDIR /app
# Ensure /tmp directory exists
RUN mkdir -p /tmp
COPY /backend .
RUN pip install --no-cache-dir -r requirements.txt
# Install Bitwarden CLI
RUN apt-get update && apt-get install -y curl jq \
    && curl -Lso /usr/local/bin/bw https://github.com/bitwarden/cli/releases/download/v1.17.0/bw-linux-1.17.0.zip \
    && chmod +x /usr/local/bin/bw

# Authenticate and retrieve secrets
RUN export BW_SESSION=$(bw login --raw) \
    && export BW_ACCESS_TOKEN=$(bw get item your_item_id | jq -r '.fields[] | select(.name=="BW_ACCESS_TOKEN").value')

COPY . .
ENV PORT 8000
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]