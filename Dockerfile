# OpenSkillVault Dockerfile
# Author: Mourad.Soltani
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
ENV FLASK_APP=backend/app.py
CMD ["gunicorn", "-b", "0.0.0.0:5000", "backend.app:app"]
# Signature: Mourad.Soltani
