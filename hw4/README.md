# Homework 04: Automatization

## OTUServer

Разработка веб‑сервера, частично реализующего протокол HTTP.

Архитектура — **Multi-threaded** на **N** воркерах. Воркеры реализованы на основе процессов с помощью модуля `multiprocessing`. На каждый запрос пользователя внутри выбранного процесса создается новый поток, в котором происходит обработка запроса и формирование ответа.


Описание параметров:

```
$ python3 httpd.py -h


usage: httpd.py [-h] [-s HOST] [-p PORT] [-w WORKERS] [-r ROOT] [-d]

OTUServer

optional arguments:
  -h, --help            show this help message and exit
  -s HOST, --host HOST  Host
  -p PORT, --port PORT  Port
  -w WORKERS, --workers WORKERS
                        Number of workers
  -r ROOT, --root ROOT  Files root directory (DOCUMENT_ROOT)
  -d, --debug           Show debug messages
```

Тесты:

```bash
# Unit-тесты
python3 httptest.py
# Нагрузочное тестирование с помощью Apache Benchmark
ab -n 50000 -c 100 -r http://127.0.0.1:8080/page.html
# Нагрузочное тестирование с помощью wrk
wrk -c100 -d5m http://127.0.0.1:8080/page.html
```

Результаты нагрузочного тестирования с помощью **Apache Benchmark** (2 воркера):

```
Benchmarking 127.0.0.1 (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        OTUServer
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /page.html
Document Length:        38 bytes

Concurrency Level:      100
Time taken for tests:   101.958 seconds
Complete requests:      50000
Failed requests:        0
Write errors:           0
Total transferred:      8850000 bytes
HTML transferred:       1900000 bytes
Requests per second:    490.40 [#/sec] (mean)
Time per request:       203.915 [ms] (mean)
Time per request:       2.039 [ms] (mean, across all concurrent requests)
Transfer rate:          84.77 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   2.1      0     137
Processing:    22  203  54.4    194     753
Waiting:       22  202  54.1    193     729
Total:         25  204  54.3    194     754

Percentage of the requests served within a certain time (ms)
  50%    267
  66%    282
  75%    295
  80%    305
  90%    366
  95%    465
  98%    676
  99%    885
 100%   1666 (longest request)
```

Результаты нагрузочного тестирования с помощью **wrk** (2 воркера):

```
Running 5m test @ http://127.0.0.1:8080/page.html
  2 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   263.28ms   68.87ms   1.36s    95.13%
    Req/Sec   193.94     96.69   444.00     63.32%
  114992 requests in 5.00m, 19.41MB read
Requests/sec:    383.48
Transfer/sec:     66.29KB
```
