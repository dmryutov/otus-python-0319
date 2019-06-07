# Homework 12: Golang

## MemcLoad v2

Go version of [memc_load.py](../hw9/memc_load.py) and [memc_load_fast.py](../hw9/memc_load_fast.py) from HW 9.



### Requirements

- Go
- Memcached



### Data to work with

Download files place them into `./data` directory.

- [https://cloud.mail.ru/public/2hZL/Ko9s8R9TA](https://cloud.mail.ru/public/2hZL/Ko9s8R9TA)
- [https://cloud.mail.ru/public/DzSX/oj8RxGX1A](https://cloud.mail.ru/public/DzSX/oj8RxGX1A)
- [https://cloud.mail.ru/public/LoDo/SfsPEzoGc](https://cloud.mail.ru/public/LoDo/SfsPEzoGc)

```bash
$ ls -lh
total 3120672
-rw-r--r--@ 1 dmryutov  staff   506M May  2 10:54 20170929000000.tsv.gz
-rw-r--r--@ 1 dmryutov  staff   506M May  2 10:28 20170929000100.tsv.gz
-rw-r--r--@ 1 dmryutov  staff   506M May  2 10:55 20170929000200.tsv.gz
```



### Install memcached

As service:

```bash
# macOS
brew install memcached
# Unix
sudo apt install memcached
# Run
memcached -l 0.0.0.0:33013,0.0.0.0:33014,0.0.0.0:33015,0.0.0.0:33016
```

As Docker container:

```bash
docker-compose up -d memcached
```


### Install dependencies

```bash
# Install packages
go get github.com/bradfitz/gomemcache/memcache
go get github.com/golang/protobuf/protoc-gen-go
```

Install `protobuf`:

```bash
# macOS
brew install protobuf
# Ubuntu
curl -OL https://github.com/google/protobuf/releases/download/v3.2.0/protoc-3.2.0-linux-x86_64.zip
unzip protoc-3.2.0-linux-x86_64.zip -d protoc3
sudo mv protoc3/bin/* /usr/local/bin/
sudo mv protoc3/include/* /usr/local/include/
```

Generate `appsinstalled.pb.go` (if you want to create project from scratch):

```bash
mkdir appsinstalled && cd appsinstalled
protoc --go_out=. appsinstalled.proto
go install appsinstalled.pb.go
```



### How to run

```bash
$ go run memc_load_fast.go -h

Usage of memc_load_fast:
  -adid string
         (default "127.0.0.1:33015")
  -attempts int
         (default 3)
  -buffer int
         (default 100)
  -dry
    
  -dvid string
         (default "127.0.0.1:33016")
  -gaid string
         (default "127.0.0.1:33014")
  -idfa string
         (default "127.0.0.1:33013")
  -log string
    
  -pattern string
         (default "/data/appsinstalled/*.tsv.gz")
  -test
    
  -workers int
         (default 5)
```

Run in Docker:

```bash
docker-compose up -d --build
```



### Testing results

**Python**

Single-threaded version:

```bash
$ time python3 memc_load.py --pattern=./data/*.tsv.gz

real	161m38.580s
user	39m2.946s
sys	104m17.116s
```

Multi-threaded version:

```bash
$ time python3 memc_load_fast.py --pattern=./data/*.tsv.gz

real	27m51.534s
user	33m18.629s
sys	18m0.636s
```

**Go**

Single-threaded version:

```bash
$ time go run memc_load.go --pattern=./data/*.tsv.gz

real	13m9.986s
user	6m22.093s
sys	6m11.167s
```

Multi-threaded version:

```bash
$ time go run memc_load_fast.go --pattern=./data/*.tsv.gz

real	4m23.219s
user	5m40.546s
sys	4m4.942s
```