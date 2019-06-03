# Homework 04: Automatization

## OTUServer

HTTP server with implemented GET and HEAD methods.

**Architecture:**

N workers (processes) from `multiprocessing` module. Each worker accepts requests concurrently, then process it and generate response.

**Server should:**

- Scale to multiple workers
- The number of workers specified in `‑w` command line argument
- Return `200`, `403` or `404` for GET and HEAD requests
- Return `405` for other requests
- Return files to an arbitrary path in `DOCUMENT_ROOT`
- `/file.html` should return the content `DOCUMENT_ROOT/file.html`
- `DOCUMENT_ROOT` is specified in `‑r` command line argument
- Return `index.html` as directory index
- `/directory/` should return `DOCUMENT_ROOT/directory/index.html`
- Return the following headers for successful GET requests: `Date`, `Server`, `Content-Length`, `Content-Type`, `Connection`
- Correct `Content‑Type` for: `.html`, `.css`, `.js`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.swf`
- Understand spaces and `%XX` in file names



### Requirements

- Python 3.x



### How to run

```bash
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

Run in Docker:

```bash
docker-compose up -d --build
```



### Testing

```bash
# Clone repository with test files
git clone https://github.com/s-stupnikov/http-test-suite www
# Unit-tests
python3 httptest.py
# Load testing with "Apache Benchmark"
ab -n 50000 -c 100 -r http://127.0.0.1:8080/httptest/dir2/page.html
# Load testing with "wrk"
wrk -c100 -d5m http://127.0.0.1:8080/httptest/dir2/page.html
```

Load testing results with **Apache Benchmark** (2 workers):

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

Document Path:          /httptest/dir2/page.html
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

Load testing results with **wrk** (2 workers):

```
Running 5m test @ http://127.0.0.1:8080/httptest/dir2/page.html
  2 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   263.28ms   68.87ms   1.36s    95.13%
    Req/Sec   193.94     96.69   444.00     63.32%
  114992 requests in 5.00m, 19.41MB read
Requests/sec:    383.48
Transfer/sec:     66.29KB
```
