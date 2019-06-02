FROM python:3.7.3-alpine3.9

RUN apk add --no-cache git build-base

WORKDIR /root

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python3"]
CMD ["/root/main.py"]
