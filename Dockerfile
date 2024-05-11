FROM python:3.9-slim

# 安装所需依赖
RUN apt-get update

# 设置工作目录
WORKDIR /app

COPY ./requirements.txt /app

RUN pip install -U pip \
    && pip --no-cache-dir install -r ./requirements.txt

COPY dags dags

RUN dbt deps