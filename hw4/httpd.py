import argparse
from datetime import datetime
import logging
import mimetypes
import multiprocessing
import os
import socket
import threading
from urllib.parse import unquote, urlparse


DOCUMENT_ROOT = 'www'
"""Default files root directory"""

CHUNK_SIZE = 1024
"""Maximum chunk size"""
HEAD_TERMINATOR = '\r\n\r\n'
"""Head section termination sequence"""

HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
RESPONSE_CODES = {
    HTTP_200_OK: 'OK',
    HTTP_400_BAD_REQUEST: 'Bad Request',
    HTTP_403_FORBIDDEN: 'Forbidden',
    HTTP_404_NOT_FOUND: 'Not Found',
    HTTP_405_METHOD_NOT_ALLOWED: 'Method Not Allowed',
}
"""Response codes"""

SERVER_NAME = 'OTUServer'
"""Server name"""
PROTOCOL = 'HTTP/1.1'
"""Protocol version"""


class HTTPRequest(object):
    """
    HTTP request handler
    """
    methods = ('GET', 'HEAD')

    def __init__(self, connection, client_address, document_root):
        """
        Args:
            connection (socket.socket): Socket connection to client
            client_address (tuple): Socket client address (host, port)
            document_root (str): Files root directory
        """
        self.worker_id = os.getpid()
        self.thread_id = threading.current_thread().name
        self.connection = connection
        self.client_address = client_address
        self.document_root = document_root
        self.request_headers = {}
        self.process_request()

    def process_request(self):
        """
        Process request - parse request, prepare and send response
        """
        try:
            request = self.receive()
            code, method, path = self.parse_request(request)
            self.send_response(code, method, path)
        except Exception:
            logging.exception('[Worker {} | {}] Error while sending response to {}'.format(
                self.worker_id, self.thread_id, self.client_address
            ))
        finally:
            logging.debug('[Worker {} | {}] Closing socket for {}'.format(
                self.worker_id, self.thread_id, self.client_address
            ))
            self.connection.close()

    def receive(self):
        """
        Receive request data

        Returns:
            str: Request data
        """
        result = ''
        while True:
            chunk = self.connection.recv(CHUNK_SIZE)
            result += chunk.decode()
            if HEAD_TERMINATOR in result or not chunk:
                break
        return result

    def parse_request(self, request):
        """
        Parse request data

        Args:
            request (str): Request data

        Returns:
            (int, str, str): (Response code, Request method, Request document path)
        """
        lines = request.split('\r\n')
        try:
            method, url, version = lines[0].split()
            method = method.upper()
        except ValueError:
            return HTTP_400_BAD_REQUEST, '?', '?'

        for line in lines[1:]:
            if not line.split():
                break
            k, v = line.split(':', 1)
            self.request_headers[k.lower()] = v.strip()

        if method not in self.methods:
            return HTTP_405_METHOD_NOT_ALLOWED, method, url

        code, path = self.parse_url(url)

        return code, method, path

    def parse_url(self, url):
        """
        Parse request url

        Args:
            url (str): Request url

        Returns:
            (int, str): (Response code, Request document path)
        """
        parsed_path = unquote(urlparse(url).path)
        path = self.document_root + os.path.abspath(parsed_path)

        is_directory = os.path.isdir(path)
        if is_directory:
            if not path.endswith('/'):
                path += '/'
            path = os.path.join(path, 'index.html')

        if not is_directory and parsed_path.endswith('/'):
            return HTTP_404_NOT_FOUND, path
        if path.endswith('/') or not os.path.isfile(path):
            return HTTP_404_NOT_FOUND, path

        return HTTP_200_OK, path

    def send_response(self, code, method, path):
        """
        Prepare and send response

        Args:
            code (int): Response code
            method (str): Request method
            path (str): Request document path
        """
        # Prepare meta info
        file_size = 0
        content_type = 'text/plain'
        body = b''
        if code == HTTP_200_OK:
            file_size = self.request_headers.get('content-length', os.path.getsize(path))
            if method == 'GET':
                content_type = mimetypes.guess_type(path)[0]
                with open(path, 'rb') as file:
                    body = file.read(file_size)

        # Prepare response
        first_line = '{} {} {}'.format(PROTOCOL, code, RESPONSE_CODES[code])
        headers = {
            'Date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Server': SERVER_NAME,
            'Connection': 'close',
            'Content-Length': file_size,
            'Content-Type': content_type,
        }
        headers = '\r\n'.join('{}: {}'.format(k, v) for k, v in headers.items())
        response = '{}\r\n{}{}'.format(first_line, headers, HEAD_TERMINATOR).encode() + body

        logging.info('[Worker {} | {}] "{} {} {}" {} {}'.format(
            self.worker_id, self.thread_id, method, path, PROTOCOL, code, file_size
        ))
        self.connection.sendall(response)


class HTTPServer(object):
    """
    HTTP server handler
    """
    def __init__(self, host, port, document_root):
        """
        Args:
            host (str): Server host
            port (int): Server port
            document_root (str): Files root directory
        """
        self.host = host
        self.port = port
        self.document_root = document_root
        self.socket = None

    def start(self):
        """
        Create socket instance and listen to host
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen()
        except socket.error as e:
            raise RuntimeError(e)

    def serve_forever(self):
        """
        Handle requests until an explicit terminate request
        """
        while True:
            connection = None
            try:
                connection, client_address = self.socket.accept()
                logging.debug('[Worker {}] Request from {}'.format(os.getpid(), client_address))
                thread = threading.Thread(
                    target=HTTPRequest,
                    args=(connection, client_address, self.document_root)
                )
                thread.daemon = True
                thread.start()
            except OSError:
                if connection:
                    connection.close()


def run_server(host, port, workers, document_root):
    """
    Run server and start workers

    Args:
        host (str): Server host
        port (int): Server port
        workers (int): Number of workers
        document_root (str): Files root directory
    """
    logging.info('Starting server at http://{}:{}'.format(host, port))
    server = HTTPServer(host, port, document_root)
    server.start()

    processes = []
    try:
        for _ in range(workers):
            process = multiprocessing.Process(target=server.serve_forever)
            processes.append(process)
            process.start()
            logging.debug('[Worker {}] Started'.format(process.pid))
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for process in processes:
            if process:
                process.terminate()
                logging.debug('[Worker {}] Terminated'.format(process.pid))


def setup_logger(debug):
    """
    Setup logger configuration

    Args:
        debug (bool): True if should show debug messages
    """
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')


def parse_arguments():
    """
    Get program arguments

    Returns:
        argparse.Namespace: Program arguments
    """
    parser = argparse.ArgumentParser(description=SERVER_NAME)
    parser.add_argument('-s', '--host', type=str, default='127.0.0.1', help='Host')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Port')
    parser.add_argument('-w', '--workers', type=int, default=1, help='Number of workers')
    parser.add_argument('-r', '--root', type=str, default=DOCUMENT_ROOT,
                        help='Files root directory (DOCUMENT_ROOT)')
    parser.add_argument('-d', '--debug', action='store_true', help='Show debug messages')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    setup_logger(args.debug)
    run_server(args.host, args.port, args.workers, args.root)
