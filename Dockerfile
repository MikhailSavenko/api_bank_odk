FROM python:3.10.7

RUN apt-get update && apt-get install -y iputils-ping

WORKDIR app/

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python", "main.py"] 