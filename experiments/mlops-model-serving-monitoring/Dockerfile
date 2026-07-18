FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "mlops_model_serving_monitoring.api:app", "--app-dir", "experiments/mlops-model-serving-monitoring/src", "--host", "0.0.0.0"]

