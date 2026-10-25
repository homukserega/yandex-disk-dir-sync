FROM python:3.12-alpine3.21

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Europe/Minsk

ARG UID=1000
ARG GID=1000

# tzdata нужен, чтобы Python/glibc-совместимые функции знали о зонах.
# Без него TZ=... игнорируется, и время остаётся в UTC.
RUN apk add --no-cache tzdata && \
    cp "/usr/share/zoneinfo/${TZ}" /etc/localtime && \
    echo "${TZ}" > /etc/timezone

RUN addgroup -g "${GID}" appuser && \
    adduser -D -u "${UID}" -G appuser appuser

WORKDIR /app
RUN chown appuser:appuser /app

COPY --chown=appuser:appuser requirements.txt ./
RUN grep -v '^ruff' requirements.txt > requirements-runtime.txt || true

RUN pip install --upgrade pip && \
    pip install -r requirements-runtime.txt && \
    rm -f requirements-runtime.txt

COPY --chown=appuser:appuser src/ ./

RUN mkdir -p data logs && chown -R appuser:appuser data logs

USER appuser

CMD ["python", "main.py"]