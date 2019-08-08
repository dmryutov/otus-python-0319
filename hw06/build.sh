#!/usr/bin/env bash

echo "=== Load settings (1/8) ==="
PROJECT_NAME=hasker
PROJECT_PATH=$(pwd)
DEBUG=False
SECRET_KEY="$(date +%s | sha256sum | base64 | head -c 50)"
POSTGRES_DB=hasker
POSTGRES_USER=hasker
POSTGRES_PASSWORD=Hasker12345


echo "=== Install packages (2/8) ==="
yum clean all
yum install -y epel-release
yum install -y https://centos7.iuscommunity.org/ius-release.rpm
yum install -y https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-oraclelinux96-9.6-3.noarch.rpm
yum install -y sudo wget git gcc-c++ make python36u python36u-devel python36u-pip nginx postgresql96-server postgresql96-contrib postgresql96-devel


echo "=== Install hack for systemd (3/8) ==="
wget https://raw.githubusercontent.com/gdraheim/docker-systemctl-replacement/master/files/docker/systemctl.py -O /usr/local/bin/systemctl
chmod +x /usr/local/bin/systemctl


echo "=== Configure PostgreSQL (4/8) ==="
export PATH="$PATH:/usr/pgsql-9.6/bin/"
postgresql96-setup initdb
echo "listen_addresses='*'" >> /var/lib/pgsql/9.6/data/postgresql.conf
sed -ie 's/ident/trust/g' /var/lib/pgsql/9.6/data/pg_hba.conf
sed -ie 's/peer/trust/g' /var/lib/pgsql/9.6/data/pg_hba.conf
sudo -u postgres /usr/pgsql-9.6/bin/pg_ctl start -D /var/lib/pgsql/9.6/data -s -o "-p 5432" -w -t 300
su postgres -c "psql -c \"CREATE USER ${POSTGRES_USER} PASSWORD '${POSTGRES_PASSWORD}'\""
su postgres -c "psql -c \"CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER}\""


echo "=== Configure Nginx (5/8) ==="
cat > /etc/nginx/conf.d/${PROJECT_NAME}.conf << EOF
server {
    listen 80;
    server_name localhost 127.0.0.1;

    access_log /var/log/nginx/${PROJECT_NAME}-access.log combined;
    error_log  /var/log/nginx/${PROJECT_NAME}-error.log error;

    location /staticfiles/ {
        alias ${PROJECT_PATH}/staticfiles/;
    }
    location /mediafiles/ {
        alias ${PROJECT_PATH}/mediafiles/;
    }
    location / {
        uwsgi_pass unix:/run/uwsgi/${PROJECT_NAME}.sock;
        include uwsgi_params;
    }
}
EOF
/usr/local/bin/systemctl enable nginx
/usr/local/bin/systemctl start nginx
/usr/local/bin/systemctl status nginx


echo "=== Configure uWSGI (6/8) ==="
mkdir -p /run/uwsgi
mkdir -p /usr/local/etc
cat > /usr/local/etc/${PROJECT_NAME}-uwsgi.ini << EOF
[uwsgi]
chdir = ${PROJECT_PATH}
chmod-socket = 666
die-on-term = true
master = true
module = main.wsgi:application
processes = 1
socket = /run/uwsgi/${PROJECT_NAME}.sock
vacuum = true

env=DJANGO_SETTINGS_MODULE=${CONFIG}
env=SECRET_KEY=${SECRET_KEY}
env=DB_NAME=${DB_NAME}
env=DB_USER=${DB_USER}
env=DB_PASSWORD=${DB_PASSWORD}
EOF


echo "=== Configure Django (7/8) ==="
pip3.6 install -r requirements.txt
for CMD in "makemigrations" "migrate" "collectstatic --link --noinput"
do
    DEBUG=${DEBUG} \
    SECRET_KEY=${SECRET_KEY} \
    POSTGRES_DB=${POSTGRES_DB} \
    POSTGRES_USER=${POSTGRES_USER} \
    POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    python3.6 manage.py ${CMD}
done


echo "=== Start Django (8/8) ==="
uwsgi --ini /usr/local/etc/${PROJECT_NAME}-uwsgi.ini &
