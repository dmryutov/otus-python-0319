FROM debian:9-slim

COPY requirements.txt /
RUN apt-get update \
    && apt-get -y --no-install-recommends install \
        gcc protobuf-c-compiler libprotobuf-c-dev zlib1g-dev \
        python3 python3-dev python3-pip python3-setuptools \
    && pip3 install --no-cache-dir -q -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN protoc-c --c_out=deviceapps/. deviceapps/deviceapps.proto
RUN python3 setup.py build_ext --inplace \
    && python3 setup.py test -q

CMD ["python3"]