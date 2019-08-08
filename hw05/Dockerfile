FROM centos/systemd

ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=on

RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm \
    && yum install -y python36u python36u-devel python36u-pip nginx gcc git rpm-build \
    && pip3.6 install uwsgi

COPY ./nginx.conf /etc/nginx
COPY ./ip2w-0.0.1-1.noarch.rpm /tmp/

RUN rpm -ihv /tmp/ip2w-0.0.1-1.noarch.rpm \
    && systemctl enable nginx.service \
    && systemctl enable ip2w.service

EXPOSE 80
CMD ["/usr/sbin/init"]
