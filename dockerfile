FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3.10 python3.10-dev python3-pip
RUN apt-get install -y ffmpeg

RUN mkdir ehrnestinho

WORKDIR /ehrnestinho

COPY . .

RUN python3 -m pip install -r requirements.txt

CMD ["python3", "-u", "bot.py"]
