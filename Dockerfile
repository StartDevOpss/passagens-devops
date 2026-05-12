# ─── Stage 1: builder ────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Copia só o requirements primeiro para aproveitar cache de camadas
COPY requirements.txt .

# Instala dependências no diretório local (sem instalar no sistema)
RUN pip install --no-cache-dir --user -r requirements.txt

# ─── Stage 2: runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Cria usuário não-root (boa prática de segurança)
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copia dependências instaladas do stage anterior
COPY --from=builder /root/.local /home/appuser/.local

# Copia o código da aplicação
COPY src/ ./src/

# Define dono dos arquivos
RUN chown -R appuser:appgroup /app

# Roda como usuário não-root
USER appuser

ENV PYTHONPATH="/app:/app/src"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check básico (garante que o container está vivo)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

CMD ["python", "src/bot.py"]
