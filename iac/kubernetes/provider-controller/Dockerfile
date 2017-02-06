FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/platform-provider-controller/deps

WORKDIR /opt/platform-provider-controller

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --root-user-action=ignore \
      --target /opt/platform-provider-controller/deps \
      -r requirements.txt

COPY controller.py .

USER 65532:65532
EXPOSE 8080

ENTRYPOINT ["python", "/opt/platform-provider-controller/controller.py"]
