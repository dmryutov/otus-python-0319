import argparse
import asyncio
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
import logging
from mimetypes import guess_extension
import pathlib
import re

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from lxml import etree


MAX_HOST_CONNECTIONS = 3
"""Number of maximum simultaneous connections to single host"""
REQUEST_TIMEOUT = 10
"""Request timeout"""
CHECK_INTERVAL = 60
"""Main page check interval (seconds)"""
DOCUMENT_ROOT = 'news'
"""Output files directory"""
MAIN_URL = 'https://news.ycombinator.com'
"""Main page URL"""
ARTICLE_URL = '{}/item?id={}'.format(MAIN_URL, '{}')
"""Single article URL"""
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Safari/605.1.15',
}
"""HTTP headers"""

URL_PATTERN = re.compile(r'^https?://')
"""Absolute URL pattern"""

Article = namedtuple('Article', ['id', 'title', 'url'])
"""Article data structure"""
HttpResponse = namedtuple('HttpResponse', ['content', 'ext'])
"""HTTP response data structure"""


def parse_arguments():
    """
    Get program arguments

    Returns:
        argparse.Namespace: Program arguments
    """
    parser = argparse.ArgumentParser(
        description='Async crawler for news.ycombinator.com (YCrawler)'
    )
    parser.add_argument('-o', '--output', type=str, default=DOCUMENT_ROOT,
                        help='Output files directory')
    parser.add_argument('-i', '--interval', type=int, default=CHECK_INTERVAL,
                        help='Main page check interval (seconds)')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Show debug messages')

    return parser.parse_args()


def setup_logger(debug):
    """
    Setup logger configuration

    Args:
        debug (bool): True if should show debug messages
    """
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')


def write_file(path, is_binary, content):
    """
    Write synchronously to file

    Args:
        path (str): File path
        is_binary (bool): True if should write binary content (e.g. images)
        content (str|byte): File content
    """
    with open(path, 'wb' if is_binary else 'w') as f:
        f.write(content)


async def fetch(url, is_binary=False):
    """
    Fetch URL and guess response extension

    Args:
        url (str): Page URL
        is_binary (bool): True if should download binary content (e.g. images)

    Returns:
        HttpResponse: HTTP response content and extension
    """
    # Fix relative link
    if not URL_PATTERN.match(url):
        url = '{}/{}'.format(MAIN_URL, url)

    logging.debug('Downloading url: {}'.format(url))
    timeout = ClientTimeout(total=REQUEST_TIMEOUT)
    connector = TCPConnector(limit_per_host=MAX_HOST_CONNECTIONS, ssl=False)
    try:
        async with ClientSession(timeout=timeout, headers=HEADERS, connector=connector) as session:
            async with session.get(url) as response:
                if is_binary:
                    content = await response.read()
                else:
                    content = await response.text()
                return HttpResponse(content, guess_extension(response.content_type))
    except Exception as e:
        logging.error('Downloading error: {} [{}]'.format(url, e))
        raise


async def download_page(url, file_dir, file_name, is_binary=False):
    """
    Fetch URL and save response to file

    Args:
        url (str): Page URL
        file_dir (pathlib.Path): File directory
        file_name (str): File name
        is_binary (bool): True if should download binary content (e.g. images)

    Returns:
        HttpResponse: HTTP response content and extension
    """
    response = await fetch(url, is_binary)
    path = file_dir.joinpath('{}{}'.format(file_name, response.ext))
    try:
        with ThreadPoolExecutor() as pool:
            await asyncio.get_running_loop().run_in_executor(
                pool, write_file, str(path), is_binary, response.content
            )
    except OSError:
        logging.error('Can\'t save file: {}'.format(path))
    return response


def article_process_status(article_id, output_dir):
    """
    Check article processing status

    Args:
        article_id (Union[int, str]): Article ID
        output_dir (pathlib.Path): Output directory

    Returns:
        bool: True if article already processed
    """
    path = output_dir.joinpath(article_id)
    return path.is_dir() and next(path.glob('article.*'), None)


def parse_main_page(content):
    """
    Parse main page and extract all articles

    Args:
        content (str): Page content

    Returns:
        list[Article]: List of top article instances
    """
    root = etree.HTML(content)
    articles = []
    for article in root.xpath('//tr[@class="athing"]'):
        link = article.xpath('.//a[@class="storylink"]')[0]
        articles.append(Article(id=article.get('id'), title=link.text, url=link.get('href')))
    return articles


def parse_comments(content):
    """
    Parse comments page and extract all links

    Args:
        content (str): Page content

    Returns:
        list[str]: List of links URLs
    """
    root = etree.HTML(content)
    return [
        link.get('href')
        for link in root.xpath('//div[@class="comment"]//a[@rel="nofollow"]')
    ]


async def handle_comments(article_id, article_dir):
    """
    Handle comments - download comments page and all links

    Args:
        article_id (int): Article ID
        article_dir (pathlib.Path): Article directory
    """
    response = await download_page(ARTICLE_URL.format(article_id), article_dir, 'detail')
    links = parse_comments(response.content)
    logging.debug('Handle comments for {}: {} links'.format(article_id, len(links)))

    tasks = [
        asyncio.create_task(download_page(link, article_dir, 'comment_{}'.format(idx), True))
        for idx, link in enumerate(links, 1)
    ]
    await asyncio.gather(*tasks)


async def handle_article(article, output_dir):
    """
    Handle article - download article page and comments

    Args:
        article (Article): Article instance
        output_dir (pathlib.Path): Output directory
    """
    logging.debug('Handle article: {} (ID {})'.format(article.title, article.id))
    article_dir = output_dir.joinpath(article.id)
    article_dir.mkdir(parents=True, exist_ok=True)

    await asyncio.gather(*[
        download_page(article.url, article_dir, 'article', True),
        handle_comments(article.id, article_dir),
    ])


async def handle_main_page(output_dir):
    """
    Handle main page - find articles and process them

    Args:
        output_dir (pathlib.Path): Output directory
    """
    response = await download_page(MAIN_URL, output_dir, 'main')
    articles = [
        article
        for article in parse_main_page(response.content)
        if not article_process_status(article.id, output_dir)
    ]
    logging.info('Handle main page: {} new articles'.format(len(articles)))

    tasks = []
    for article in articles:
        tasks.append(asyncio.create_task(handle_article(article, output_dir)))
        # Site blocks too frequent requests and shows message:
        # "Sorry, we're not able to serve your requests this quickly."
        await asyncio.sleep(1)
    await asyncio.gather(*tasks)


async def monitor_main(output_dir, interval):
    """
    Monitor main page for new top posts

    Args:
        output_dir (pathlib.Path): Output directory
        interval (int): Main page check interval (seconds)
    """
    while True:
        try:
            await asyncio.wait_for(handle_main_page(output_dir), timeout=interval)
        except Exception as e:
            logging.error('Crawler failed: {}'.format(e))
        await asyncio.sleep(interval)


if __name__ == '__main__':
    args = parse_arguments()
    setup_logger(args.debug)

    result_dir = pathlib.Path(args.output)
    result_dir.mkdir(parents=True, exist_ok=True)

    try:
        asyncio.run(monitor_main(result_dir, args.interval))
    except asyncio.CancelledError:
        logging.info('Crawler canceled')
    except KeyboardInterrupt:
        logging.info('Crawler stopped')
