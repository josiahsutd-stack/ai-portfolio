FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "projects/ai-aec-job-fit-analyzer/app.py", "--server.address=0.0.0.0"]

