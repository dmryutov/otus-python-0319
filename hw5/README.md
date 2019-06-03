# Homework 05: Web

## uWSGI daemon

Implementation of uWSGI daemon (for CentOS 7), which should determine user city by given IP (IPv4) and return current weather in this location in JSON format.

**Service should:**

- Use external services:
    - IP location: [https://ipinfo.io/developers](https://ipinfo.io/developers)
    - Current weather: [https://openweathermap.org/current](https://openweathermap.org/current)
- Nginx should proxy requests to daemon
- Systemd should start daemon
- Daemon should be built into rpm-package



### Requirements

- Python 3.x
- systemd
- nginx



### Install dependencies

```bash
pip3 install -r requirements.txt
```



### How to run

Build rpm package:

```bash
chmod +x buildrpm.sh
./buildrpm.sh $PWD/ip2w.spec
```

Run daemon:

```bash
systemctl start ip2w
```

Stop daemon:

```bash
systemctl stop ip2w
```

Run in Docker:

```bash
docker-compose up -d --build
```



### Testing

```bash
python3 tests.py
```



### Request example

```bash
$ curl http://localhost/ip2w/178.219.186.12
# {"city": "Mytishchi", "temp": "+6.95", "conditions": "ясно"}
```