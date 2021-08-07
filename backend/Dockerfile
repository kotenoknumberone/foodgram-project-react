FROM python:3.7.3
WORKDIR /code
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
