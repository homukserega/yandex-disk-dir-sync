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

# COPY --chown=appuser:appuser requirements.txt ./
# Для исключения падения сервиса ставятся только строго определеннные зависимости
# а не зависимости из requirements.txt
# Если нужно - можно поменять установку из requirements в контейнере с --no-deps \...
# на -r ewquirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --no-deps \
    certifi charset-normalizer idna python-dotenv requests urllib3 loguru

COPY --chown=appuser:appuser src/ ./
COPY --chown=appuser:appuser .env ./

RUN mkdir data logs && chown -R 1000:1000 data logs

USER appuser

CMD ["python", "main.py"]
