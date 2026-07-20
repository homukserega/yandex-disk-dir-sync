FROM python:3.12.3-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG UID=1000
ARG GID=1000

# Создаём пользователя и группу (Alpine-синтаксис)
RUN addgroup -g ${GID} appuser && \
    adduser -D -u ${UID} -G appuser appuser

WORKDIR /app
RUN chown appuser:appuser /app

COPY --chown=appuser:appuser requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r <(grep -v "^ruff" requirements.txt)

COPY --chown=appuser:appuser src/ ./
COPY --chown=appuser:appuser .env ./

RUN mkdir data logs && chown -R 1000:1000 data logs

USER appuser

CMD ["python", "main.py"]
