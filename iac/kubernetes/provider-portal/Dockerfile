FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /opt/platform-provider-portal
COPY app.py .

USER 65532:65532
EXPOSE 8080

ENTRYPOINT ["python", "/opt/platform-provider-portal/app.py"]
