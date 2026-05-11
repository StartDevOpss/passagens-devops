FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Isso garante que os logs apareçam no Kubernetes
ENV PYTHONUNBUFFERED=1 
CMD ["python", "bot.py"]