FROM python:3.9-slim
WORKDIR /app

# 1. Copia apenas o necessário para instalar dependências (otimiza cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. COPIA TODO O RESTANTE DO PROJETO (Isso leva a pasta /src para dentro)
COPY . . 

# 3. Define as variáveis e o comando de inicialização
ENV PYTHONPATH="/app:/app/src"
# Mude para o caminho correto que o seu comando ls mostrou:
CMD ["python", "src/bot.py"]