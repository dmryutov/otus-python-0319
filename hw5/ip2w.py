from configparser import ConfigParser
import json
import logging
import os
import socket
import time

import requests

HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_500_INTERNAL_ERROR = 500
"""Response codes"""

CONFIG_PATH = '/usr/local/etc/ip2w.ini'
"""Configuration file path"""
IP_URL = 'https://ipinfo.io/{}'
"""IP service url"""
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&lang=ru&APPID={}'
"""Weather service url"""


def load_config(env):
    """
    Load and parse program configuration

    Args:
        env (dict): Environment variables

    Returns:
        dict: Program configuration
    """
    config = ConfigParser()
    config.read(CONFIG_PATH)
    config = {
        'log_path': config['uwsgi']['log-path'],
        'retries': int(config['uwsgi']['retries']),
        'timeout': int(config['uwsgi']['timeout']),
        'api_key': os.environ.get('API_KEY'),
        'path_info': env.get('PATH_INFO', ''),
        'remote_addr': env.get('REMOTE_ADDR', ''),
    }
    return config


def setup_logger(log_path):
    """
    Setup logger configuration

    Args:
        log_path (str): Log file path
    """
    logging.basicConfig(filename=log_path,
                        level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')


def perform_request(url, config):
    """
    Perform HTTP request to external API

    Args:
        url (str): Service url
        config (dict): Program configuration

    Returns:
        (int, Union[dict, str]): (Response code, Response data)
    """
    for attempt in range(config['retries']):
        try:
            response = requests.get(url, timeout=config['timeout'])
            response.raise_for_status()
            return HTTP_200_OK, response.json()
        except requests.exceptions.RequestException:
            time.sleep(1)
    return HTTP_500_INTERNAL_ERROR, 'Maximum retries limit to API exceeded'


def get_ip(config):
    """
    Extract request IP

    Args:
        config (dict): Program configuration

    Returns:
        (int, str): (Response code, Request IP)
    """
    try:
        request = config['path_info'].strip('/').split('/')
        if len(request) > 2:
            raise socket.error
        elif len(request) == 2:
            ip = request[1]
        else:
            ip = config['remote_addr']

        socket.inet_aton(ip)
        return HTTP_200_OK, ip
    except socket.error:
        return HTTP_400_BAD_REQUEST, 'Invalid IP'


def get_city_by_ip(ip, config):
    """
    Get city by request IP

    Args:
        ip (str): Request IP
        config (dict): Program configuration

    Returns:
        (int, str): (Response code, City)
    """
    code, response = perform_request(IP_URL.format(ip), config)
    if code != HTTP_200_OK:
        return code, response

    city = response.get('city')
    country = response.get('country')
    if not (city and country):
        return HTTP_500_INTERNAL_ERROR, 'Invalid API response'

    return HTTP_200_OK, '{},{}'.format(city, country)


def get_weather_by_city(city, config):
    """
    Get information about current weather in selected city

    Args:
        city (str): City
        config (dict): Program configuration

    Returns:
        (int, str): (Response code, Request IP)
    """
    code, response = perform_request(WEATHER_URL.format(city, config['api_key']), config)
    if code != HTTP_200_OK:
        return code, response

    if response.get('cod') != HTTP_200_OK:
        return HTTP_500_INTERNAL_ERROR, response.get('message')

    temp = str(response['main']['temp'])
    conditions = ', '.join([condition['description'] for condition in response['weather']])
    weather = {
        'city': response['name'],
        'temp': temp if temp.startswith('-') else '+' + temp,
        'conditions': conditions,
    }
    return HTTP_200_OK, weather


def load_weather_data(config):
    """
    Get information about current weather

    Args:
        config (dict): Program configuration

    Returns:
        (int, Union[dict, str]): (Response code, Weather data)
    """
    code, ip = get_ip(config)
    if code != HTTP_200_OK:
        return code, ip

    code, city = get_city_by_ip(ip, config)
    if code != HTTP_200_OK:
        return code, city

    code, weather = get_weather_by_city(city, config)
    return code, weather


def application(env, start_response):
    """
    WSGI application

    Args:
        env (dict): Environment variables
        start_response (Callable[str, list]): Start response function

    Returns:
        list: Response data
    """
    config = load_config(env)
    setup_logger(config['log_path'])
    logging.info('Request: {}'.format(config['path_info']))

    code, response = load_weather_data(config)
    logging.info('Response: {}, {}'.format(code, response))
    if not isinstance(response, str):
        response = json.dumps(response, ensure_ascii=False)

    start_response(str(code), [
        ('Content-Type', 'application/json; charset=UTF-8'),
    ])
    return [response.encode()]
