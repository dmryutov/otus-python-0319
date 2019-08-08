# Homework 09: Concurrency

## MemcLoad

Fast version of [memc_load.py](memc_load.py).

**Task:**

- Rewrite single-threaded version of loader to more productive version
- Preserve chronological order of files when renaming processed ones

**Architecture:**

Multi-threading with multiple threads.

Main process creates **N** workers. For each memcached address worker creates thread for writing logs. Each worker parses given log file info about user's installed apps and adds to writing queue. At the end of file worker sends `SENTINEL` (stop) signal to all threads and waits for total result (number of processed/failed lines).



### Requirements

- Python 3.x
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
pip3 install -r requirements.txt
```

Generate `appsinstalled_pb2.py` (if you want to create project from scratch):

```bash
cd appsinstalled
protoc --python_out=. appsinstalled.proto
```



### How to run

```bash
$ python3 memc_load_fast.py -h

Usage: memc_load_fast.py [options]

optional arguments:
  -h, --help            show this help message and exit
  -t, --test            
  -l LOG, --log=LOG     
  --dry                 
  --pattern=PATTERN     
  --idfa=IDFA           
  --gaid=GAID           
  --adid=ADID           
  --dvid=DVID           
  -w WORKERS, --workers=WORKERS
  -a ATTEMPTS, --attempts=ATTEMPTS
```

Run in Docker:

```bash
docker-compose up -d --build
```



### Testing results

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
