# Homework 09: Concurrency

## MemcLoad

Переделка однопоточной версии memc_load.py в более производительный вариант.

Архитектура — **Multi-threaded** на **N** воркерах. Воркеры реализованы на основе процессов с помощью модуля `multiprocessing`.

Необходимые сервисы:

- Memcached

Установка зависимостей:

```bash
pip3 install -r requirements.txt
```

Описание параметров:

```
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

Однопоточная версия:

```bash
$ time python3 memc_load.py --pattern=./data/*.tsv.gz

real	161m38.580s
user	39m2.946s
sys	104m17.116s
```

Многопоточная версия:

```bash
$ time python3 memc_load_fast.py --pattern=./data/*.tsv.gz

real	27m51.534s
user	33m18.629s
sys	18m0.636s
```
