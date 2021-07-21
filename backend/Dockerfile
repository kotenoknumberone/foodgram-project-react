FROM python:3.8.5
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
CMD python /code/manage.py runserver 127.0.0.1:8000 
