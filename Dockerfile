FROM python:3.8-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
RUN apk add --no-cache gcc g++ linux-headers
RUN mkdir -p /usr/main/data/images/ && mkdir -p /usr/main/data/temp/ && mkdir -p /usr/main/data/db/
WORKDIR /usr/main/

COPY requirements.txt /usr/main/
#RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip setuptools wheel
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt

COPY app /usr/main/app
COPY ui /usr/main/ui
COPY main.py /usr/main/


EXPOSE 8002

VOLUME ["/usr/main/content/db", "/usr/main/content/file", "/usr/main/content/temp"]
CMD ["python", "main.py"]