FROM python:3.10.2-slim-buster
ADD . /alice_app
WORKDIR /alice_app
RUN pip install wheel
RUN pip install -r requirements.txt
CMD ["python", "main.py"]