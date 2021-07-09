FROM python:3.9.1

WORKDIR /unique_people_etl
COPY requirements.txt .
RUN pip install -r requirements.txt --user --pre