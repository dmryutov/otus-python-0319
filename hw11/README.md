# Homework 11: YCrawler

## YCrawler

Async crawler for [news.ycombinator.com](https://news.ycombinator.com).

**Script should:**

- Crawl top 30 news from root page with specified interval
- Download and save news pages
- Download and save pages by links in comments to news
- Download pages non-recursively
- Download pages without requisites (css/img/js/etc)
- Use standard library and `aiohttp`



### Requirements

- Python 3.x



### Install dependencies

```bash
pip3 install -r requirements.txt
```



### How to run

```bash
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

Run in Docker:

```bash
docker-compose up -d --build
```