FROM python:3.6-alpine

LABEL maintainer="patrick@kite4fun.nl"

ENV SERVERIP 0.0.0.0

RUN apk update \
  && apk add gcc python-dev libc-dev libffi-dev openssl-dev jpeg-dev zlib-dev freetype-dev

COPY requirements.txt /
RUN pip install -r requirements.txt && mkdir /app

COPY app.py /app/
COPY static /app/static
COPY templates /app/templates
COPY *.LICENSE /app/
WORKDIR /app

EXPOSE 5000

CMD ["python", "app.py"]
