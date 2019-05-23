FROM python:3.7.3-alpine3.9


WORKDIR /root

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

ENTRYPOINT ["python3"]
CMD ["/root/server.py"]
