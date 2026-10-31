FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy only the app so .env never ends up in the image
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]
