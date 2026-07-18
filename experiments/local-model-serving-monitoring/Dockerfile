FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "local_model_serving_monitoring.api:app", "--app-dir", "experiments/local-model-serving-monitoring/src", "--host", "0.0.0.0"]

