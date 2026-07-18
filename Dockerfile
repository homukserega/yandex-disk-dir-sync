FROM python:3.12.3-alpine

# Аргументы для UID/GID (значения по умолчанию — 1000)
ARG UID=1000
ARG GID=1000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаём пользователя с фиксированным UID/GID
RUN groupadd -g ${GID} appuser && \
    useradd -m -u ${UID} -g appuser appuser

WORKDIR /app
RUN chown appuser:appgroup /app

COPY --chown=appuser:appgroup requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appgroup src/ ./
COPY --chown=appuser:appgroup .env ./

RUN mkdir data logs && chown -R appuser:appgroup data logs

USER appuser

CMD ["python", "main.py"]
