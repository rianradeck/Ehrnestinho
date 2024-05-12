FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3.10 python3.10-dev python3-pip

RUN mkdir ehrnestinho

WORKDIR /ehrnestinho

COPY requirements.txt .

RUN python3 --version

RUN python3 -m pip install -r requirements.txt

COPY . .

CMD ["python3", "-u", "bot.py"]
