FROM python:3.8

WORKDIR /src
COPY . .
RUN pip install -r requirements.txt

CMD ["python","server.py"]
