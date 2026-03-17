FROM python:3.11-slim

WORKDIR /auth_app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . /auth_app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
