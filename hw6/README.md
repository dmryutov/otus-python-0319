# Homework 06: Django Project

## Hasker: Poor Man's Stackoverflow

Разработка Q&A сайта, аналога stackoverflow.com

Запуск контейнера:

```bash
docker pull centos
docker run -it --rm -p 8000:80 centos /bin/bash
```

Подготовка:

```bash
yum clean all
yum install -y git make
git clone https://github.com/dmryutov/otus-python-0319.git projects/otus
cd projects/otus/hw6
```

Сборка проекта:

```bash
chmod +x build.sh
make prod
```