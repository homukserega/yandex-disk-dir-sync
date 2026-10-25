FROM python:3.12-alpine3.21

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

ARG UID=1000
ARG GID=1000

# Создаём пользователя и группу (Alpine-синтаксис)
RUN addgroup -g "${GID}" appuser && \
    adduser -D -u "${UID}" -G appuser appuser

WORKDIR /app
RUN chown appuser:appuser /app

# requirements без ruff — собираем отдельный файл в POSIX-шелле,
# чтобы не зависеть от bash process substitution
COPY --chown=appuser:appuser requirements.txt ./
RUN grep -v '^ruff' requirements.txt > requirements-runtime.txt || true

RUN pip install --upgrade pip && \
    pip install -r requirements-runtime.txt && \
    rm -f requirements-runtime.txt

COPY --chown=appuser:appuser src/ ./

RUN mkdir -p data logs && chown -R appuser:appuser data logs

USER appuser

CMD ["python", "main.py"]