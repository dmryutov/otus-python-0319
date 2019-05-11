# Homework 11: YCrawler

## YCrawler

Разработка асинхронного краулера для новостного сайта [news.ycombinator.com](https://news.ycombinator.com).

Установка зависимостей:

```bash
pip3 install -r requirements.txt
```

Описание параметров:

```
$ python3 ycrawler.py -h


usage: ycrawler.py [-h] [-o OUTPUT] [-i INTERVAL] [-d]

Async crawler for news.ycombinator.com (YCrawler)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output files directory
  -i INTERVAL, --interval INTERVAL
                        Main page check interval (seconds)
  -d, --debug           Show debug messages

```
