FROM python:3.8-alpine


RUN mkdir -p /usr/main/content/file/ && mkdir -p /usr/main/content/temp/
WORKDIR /usr/main/

COPY requirements.txt /usr/main/
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt

COPY app /usr/main/app
COPY front /usr/main/front
COPY main.py /usr/main/


EXPOSE 8002

VOLUME ["/usr/main/content"]
CMD ["python", "main.py"]