FROM python:3.12.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install debugpy

COPY . .

EXPOSE 8000
EXPOSE 5678

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]