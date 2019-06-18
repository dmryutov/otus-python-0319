FROM centos

WORKDIR /app

RUN yum clean all \
    && yum install -y git make gcc-c++ vim ssh
RUN git clone https://github.com/python/cpython.git . \
    && git checkout 2.7 \
    && ./configure --with-pydebug --prefix=/app