FROM debian

RUN apt-get update && \
    apt-get install -y git texlive-base texlive-bibtex-extra \
                       texlive-pstricks python3 python3-pip && \
    apt-get clean

ADD requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

ENV PYTHONPATH /src

ADD rasm /src/rasm/

WORKDIR /workdir

ENTRYPOINT ["python3", "-m", "rasm"]
