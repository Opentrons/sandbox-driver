FROM vimagick/alpine-arm:3.3
#COPY qemu-arm-static /usr/bin/qemu-arm-static

RUN apk update && \
    apk add \
    ca-certificates \
    python3 \
    wget

RUN apk del wget ca-certificates && rm -rf /var/cache/apk/*

RUN apk update && apk add \
    build-base \ 
    ca-certificates \
    libffi-dev \ 
    python3 \
    python3-dev \
    wget \ 
    && wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python3

WORKDIR /home/sandbox-driver

RUN pip3 install autobahn==0.10.3

RUN rm -rf /var/cache/apk/*
#ENTRYPOINT ["tar", "-cvz", "/usr/lib/python3.5/site-packages/", "/home/sandbox-driver"]
#ENTRYPOINT ["python3", "driver/driver_client.py"]
ENTRYPOINT ["bash"]
