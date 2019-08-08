import argparse
from collections import defaultdict, namedtuple
from datetime import datetime
import gzip
import json
import logging
from operator import itemgetter
import pathlib
import re
from statistics import median


DEFAULT_CONFIG_PATH = './config.json'
"""Default configuration file path"""
DEFAULT_CONFIG = {
    'REPORT_SIZE': 1000,
    'REPORT_DIR': './reports',
    'LOG_DIR': './log',
    'LOG_FILE': None,
    'ERROR_PERCENT': 10,
}
"""Program default configuration"""
LOG_FILE_MASK = re.compile(r'^nginx-access-ui\.log-(\d{8})(\.gz)?$')
"""Log file name pattern"""
LOG_LINE_MASK = re.compile(
    r'([\d\.]+)\s'
    r'(\S*)\s+'
    r'(\S*)\s'
    r'\[(.*?)\]\s'
    r'"(.*?)"\s'
    r'(\d+)\s'
    r'(\S*)\s'
    r'"(.*?)"\s'
    r'"(.*?)"\s'
    r'"(.*?)"\s'
    r'"(.*?)"\s'
    r'"(.*?)"\s'
    r'(\d+\.\d+)\s*'
)
"""
Log file correct line pattern
Line structure:
```
$remote_addr
$remote_user
$http_x_real_ip
[$time_local]
"$request"
$status
$body_bytes_sent
"$http_referer"
"$http_user_agent"
"$http_x_forwarded_for"
"$http_X_REQUEST_ID"
"$http_X_RB_USER"
$request_time
```
"""
LogFile = namedtuple('LogFile', ['path', 'date', 'ext'])
"""Log file data structure"""
LogLine = namedtuple('LogLine', ['url', 'request_time'])
"""Log file line data structure"""


def get_config_path():
    """
    Get program configuration file path (from program arguments or from default settings)

    Returns:
        str: Configuration file path
    """
    parser = argparse.ArgumentParser(description='Log Analyzer')
    parser.add_argument('-c', '--config', help='Path to config file')
    args = parser.parse_args()

    config_path = args.config if args.config else DEFAULT_CONFIG_PATH
    return config_path


def load_config():
    """
    Load program configuration and concatenate with default config

    Returns:
        dict: Program configuration

    Raises:
        TypeError: If configuration is not a dictionary
    """
    config_path = get_config_path()
    with open(config_path, 'r') as f:
        config = json.load(f)

    if not isinstance(config, dict):
        raise TypeError('Configuration is not a dictionary')
    return {
        **DEFAULT_CONFIG,
        **config
    }


def setup_logger(log_path):
    """
    Setup logger configuration - to file if `LOG_FILE` is set, else - to stdout

    Args:
        log_path (str): Log file path
    """
    logging.basicConfig(filename=log_path,
                        level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')


def get_latest_log_file(log_dir):
    """
    Find latest (with biggest date in name) log file

    Args:
        log_dir (pathlib.Path): Log files directory path

    Returns:
        LogFile: Log file

    Raises:
        FileNotFoundError: If log directory does not exists or is not directory
    """
    if not (log_dir.exists() and log_dir.is_dir()):
        raise FileNotFoundError('Log directory does not exists')

    log_file = None
    for path in log_dir.iterdir():
        matches = re.findall(LOG_FILE_MASK, path.name)
        if not matches:
            continue
        date, ext = matches[0]

        try:
            log_date = datetime.strptime(date, '%Y%m%d').date()
        except ValueError:
            continue

        if not log_file or log_file.date < log_date:
            log_file = LogFile(path, log_date, ext)

    return log_file


def get_report_path(log_file, report_dir):
    """
    Generate report file path

    Args:
        log_file (LogFile): Log file
        report_dir (pathlib.Path): Report directory path

    Returns:
        pathlib.Path: Report file path

    Raises:
        FileNotFoundError: If report directory does not exists or is not directory
    """
    if not report_dir.exists() or not report_dir.is_dir():
        raise FileNotFoundError('Report directory does not exists')

    report_date = log_file.date.strftime('%Y.%m.%d')
    report_path = report_dir.joinpath('report-{}.html'.format(report_date))
    return report_path


def parse_line(line):
    """
    Parse log file single line

    Args:
        line (str): Log file line

    Returns:
        LogLine: Request data
    """
    match = LOG_LINE_MASK.findall(line)
    if not match:
        return None

    url = match[0][4]
    request_time = match[0][-1]
    if not (url and request_time):
        return None
    return LogLine(url, float(request_time))


def parse_log_file(log_file):
    """
    Parse log file and extract information about requests line by line

    Args:
        log_file (LogFile): Log file

    Returns:
        LogLine: Single request data
    """
    if log_file.ext == '.gz':
        f = gzip.open(log_file.path.absolute(), 'rt')
    else:
        f = open(str(log_file.path), encoding='utf-8')

    with f:
        for line in f:
            yield parse_line(line)


def extract_info_from_file(log_file, error_percent):
    """
    Extract information about requests from log file

    Args:
        log_file (LogFile): Log file
        error_percent (float): Error max percent

    Returns:
        dict: Request data

    Raises:
        ValueError: If log errors limit was exceeded
    """
    lines = 0
    fails = 0
    requests = defaultdict(list)
    for request in parse_log_file(log_file):
        lines += 1
        if request:
            requests[request.url].append(request.request_time)
        else:
            fails += 1

    # Check error percentage
    errors = 100 * fails / lines
    if errors > error_percent:
        raise ValueError('Log errors limit was exceeded. Error percent {}% more than {}%'.format(
            errors, error_percent
        ))
    return requests


def prepare_report_data(requests, report_size):
    """
    Process request statistics and generate report data

    Args:
        requests (dict) :
        report_size (int): Maximum report size

    Returns:
        List: Report data
    """
    total_count = 0
    total_time = 0.0
    for request_times in requests.values():
        total_count += len(request_times)
        total_time += sum(request_times)

    report_data = []
    for url, request_times in requests.items():
        request_count = len(request_times)
        request_time = sum(request_times)
        report_data.append({
            'url': url,
            'count': request_count,
            'count_perc': round(100.0 * request_count / float(total_count), 3),
            'time_sum': round(sum(request_times), 3),
            'time_perc': round(100.0 * request_time / total_time, 3),
            'time_avg': round(request_time / request_count, 3),
            'time_max': round(max(request_times), 3),
            'time_med': round(median(request_times), 3),
        })
    report_data = sorted(report_data, key=itemgetter('time_sum'), reverse=True)
    report_data = report_data[:report_size]

    return report_data


def create_report(report_data, report_dir, log_date):
    """
    Save report data to HTML file

    Args:
        report_data (list): Report data
        report_dir (pathlib.Path): Report directory path
        log_date (datetime.date): Log file data

    Returns:
        pathlib.Path: Report file path
    """
    report_date = log_date.strftime('%Y.%m.%d')
    report_path = report_dir.joinpath('report-{}.html'.format(report_date))

    with open('report.html', 'r', encoding='utf-8') as f:
        template = f.read()
        template = template.replace('$table_json', json.dumps(report_data))
    with open(str(report_path), 'w', encoding='utf-8') as f:
        f.write(template)

    return report_path


def main():
    config = load_config()
    setup_logger(config.get('LOG_FILE'))

    # 1. Get log file instance
    log_dir = pathlib.Path(config.get('LOG_DIR'))
    log_file = get_latest_log_file(log_dir)
    if not log_file:
        logging.info('No logs in "{}"'.format(log_file))
        return

    # 2. Get report file path
    report_dir = pathlib.Path(config.get('REPORT_DIR'))
    report_path = get_report_path(log_file, report_dir)
    if report_path.exists():
        logging.info('Report for "{}" already exists'.format(log_file.date))
        return

    # 3. Extract logs and create report
    requests = extract_info_from_file(log_file, config.get('ERROR_PERCENT'))
    report_data = prepare_report_data(requests, config.get('REPORT_SIZE'))
    report_path = create_report(report_data, report_dir, log_file.date)

    logging.info('Report "{}" from file "{}" was created successfully'.format(
        report_path, log_file.path
    ))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.exception(e)
