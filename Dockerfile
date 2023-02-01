FROM python:3.8
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
COPY . /app/
CMD alembic upgrade head; uvicorn main:app --host 0.0.0.0 --port 8000