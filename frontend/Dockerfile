# frontend/Dockerfile
FROM python:3.9-slim
WORKDIR /app
# Ensure /tmp directory exists
RUN mkdir -p /tmp
COPY /frontend .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT 8080
ENV BACKEND_API_URL=http://backend.jamesstaud.com:8000/query
EXPOSE 8080
CMD ["python", "app.py"]