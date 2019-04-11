# Homework 05: Web

## uWSGI daemon

Разработка uWSGI демона (для CentOS 7), который по запросу на IPv4 адрес возвращает текущую погоду в
городе, к которому относится IP, в виде json.

Необходимые сервисы:

- systemd
- nginx

Установка зависимостей:

```bash
pip3 install -r requirements.txt
```

Сборка rpm пакета:

```bash
chmod +x buildrpm.sh
./buildrpm.sh $PWD/ip2w.spec
```

Запуск демона:

```bash
systemctl start ip2w
```

Остановка демона:

```bash
systemctl stop ip2w
```

Тесты:

```bash
python3 tests.py
```

Пример запроса:

```bash
$ curl http://localhost/ip2w/178.219.186.12
{"city": "Mytishchi", "temp": "+6.95", "conditions": "ясно"}
```