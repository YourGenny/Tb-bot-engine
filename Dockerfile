FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY terabox.py .

ENV PORT=10000
ENV RENDER=true

CMD ["gunicorn", "terabox:app", "--bind", "0.0.0.0:10000", "--workers", "2", "--threads", "4", "--timeout", "60"]