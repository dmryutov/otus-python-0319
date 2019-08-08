from abc import abstractmethod
from datetime import datetime
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging
from optparse import OptionParser
import os
import uuid

from scoring import get_score, get_interests
from store import Store, RedisStorage


SALT = 'Otus'
ADMIN_LOGIN = 'admin'
ADMIN_SALT = '42'

OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: 'Bad Request',
    FORBIDDEN: 'Forbidden',
    NOT_FOUND: 'Not Found',
    INVALID_REQUEST: 'Invalid Request',
    INTERNAL_ERROR: 'Internal Server Error',
}

UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: 'unknown',
    MALE: 'male',
    FEMALE: 'female',
}


class AgeLimitError(ValueError):
    pass


class PhoneFormatError(ValueError):
    pass


class FieldBase(object):
    """
    Field base class
    """
    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable

    @abstractmethod
    def validate(self, value):
        """
        Validate field value

        Args:
            value: Field value
        """
        pass

    def to_python(self, value):
        """
        Convert value to Python structures

        Args:
            value: Field value

        Returns:
            Field value in some representation
        """
        return value


class CharField(FieldBase):
    """
    Char field
    """
    def validate(self, value):
        """
        Validate field value. Validation rules:
            1) String

        Args:
            value: Field value
        """
        super().validate(value)

        if not isinstance(value, str):
            raise TypeError('Field value should be a string')


class ArgumentsField(FieldBase):
    """
    Arguments field
    """
    def validate(self, value):
        """
        Validate field value. Validation rules:
            1) Dictionary

        Args:
            value: Field value
        """
        super().validate(value)

        if not isinstance(value, dict):
            raise TypeError('Field value should be a dictionary')


class EmailField(CharField):
    """
    Email field
    """
    def validate(self, value):
        """
        Validate field value. Validation rules:
            1) String
            2) Should contain '@' character

        Args:
            value: Field value
        """
        super().validate(value)

        if '@' not in value:
            raise TypeError('Field value should contain "@" character')


class PhoneField(FieldBase):
    """
    Phone field
    """

    def validate(self, value):
        """
        Validate field value. Validation rules:
            1) String or number
            2) Length - 11
            2) First character - '7'

        Args:
            value: Field value
        """
        super().validate(value)

        if not isinstance(value, (str, int)):
            raise TypeError('Field value should be a string or a number')

        val = str(value)
        if len(val) != 11:
            raise PhoneFormatError('Field value length should be 11 characters')
        if not val.startswith('7'):
            raise PhoneFormatError('Field value should starts with "7"')


class DateField(CharField):
    """
    Date field
    """
    @staticmethod
    def to_date(value):
        """
        Convert field value from string to date object

        Args:
            value (str): Field value (string)

        Returns:
            datetime.datetime: Field value (date)
        """
        return datetime.strptime(value, '%d.%m.%Y')

    def validate(self, value):
        """
        Validate field value. Validation rules:
            1) String
            2) Format - DD.MM.YYYY

        Args:
            value: Field value
        """
        super().validate(value)

        try:
            self.to_date(value)
        except (ValueError, TypeError):
            raise ValueError('Field value should be in DD.MM.YYYY format')

    def to_python(self, value):
        """
        Convert value to datetime structure

        Args:
            value: Field value

        Returns:
            Field value in datetime representation
        """
        try:
            return self.to_date(value)
        except (ValueError, TypeError):
            return value


class BirthDayField(DateField):
    """
    Birthday field
    """
    def validate(self, value):
        """
        Validate field value. Validation rules:
            1) Date
            2) 0 < Now - value <= 70 years

        Args:
            value: Field value
        """
        super().validate(value)

        age = (datetime.now() - self.to_date(value)).days / 365
        if not (0 < age <= 70):
            raise AgeLimitError('Age should be in range 0 < age <= 70')


class GenderField(FieldBase):
    """
    Gender field
    """

    def validate(self, value):
        """
        Validate field value. Validation rules:
            1) Number
            2) Value in (0, 1, 2)

        Args:
            value: Field value
        """
        super().validate(value)

        if not isinstance(value, int):
            raise TypeError('Field should be a number')
        if value not in GENDERS:
            raise ValueError('Field value should be in (0, 1, 2)')


class ClientIDsField(FieldBase):
    """
    Client IDs field
    """

    def validate(self, value):
        """
        Validate field value. Validation rules:
            1) Array
            2) Elements - number

        Args:
            value: Field value
        """
        super().validate(value)

        if not isinstance(value, list):
            raise TypeError('Field should be a list')
        if not value:
            raise ValueError('Field value can not be empty')
        if not all(isinstance(item, int) for item in value):
            raise TypeError('Field value items should be numbers')


class RequestMeta(type):
    """
    Request handler metaclass
    """
    def __new__(cls, name, bases, attrs):
        fields = {
            key: field
            for key, field in attrs.items()
            if isinstance(field, FieldBase)
        }
        for key in fields:
            del attrs[key]
        attrs['fields'] = fields
        return super().__new__(cls, name, bases, attrs)


class RequestBase(metaclass=RequestMeta):
    """
    Request handler base class
    """
    def __init__(self, body):
        self.errors = {}
        self.body = body

    def is_empty(self, name):
        """
        Check if field value is empty

        Args:
            name (str): Field name

        Returns:
            bool: True if field value is empty
        """
        return getattr(self, name, None) in (None, '', [], {}, ())

    def is_valid(self):
        """
        Check if all request fields are valid

        Returns:
            bool: True if all request fields are valid
        """
        self.validate()
        return not self.errors

    def validate(self):
        """
        Validate request fields
        """
        for name, field in self.fields.items():
            value = self.body.get(name)
            setattr(self, name, value)
            # Check `required` parameter
            if field.required and value is None:
                self.errors[name] = 'Field is required'
                continue
            # Check `nullable` parameter
            if not field.nullable and self.is_empty(name):
                self.errors[name] = 'Field value can not be null'
                continue
            # Skip check if None (may crush `isinstance` check or casting to date)
            elif value is None:
                continue
            # Check request arguments
            try:
                field.validate(value)
            except (TypeError, ValueError) as e:
                self.errors[name] = str(e)
            # Convert value to some field representation
            setattr(self, name, field.to_python(value))

    def format_errors(self):
        """
        Format validation errors

        Returns:
            str: Validation errors
        """
        return str(self.errors)


class ClientsInterestsRequest(RequestBase):
    """
    Clients interests request
    """
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(RequestBase):
    """
    Online scoring request
    """
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)
    pairs = (
        ('phone', 'email'),
        ('first_name', 'last_name'),
        ('gender', 'birthday'),
    )
    empty_values = (None, '', [], {}, ())

    def validate(self):
        """
        Validate request fields and check that request contains at least one
        pair of non-empty fields
        """
        super().validate()

        has_pair = any(
            not self.is_empty(pair[0]) and not self.is_empty(pair[1])
            for pair in self.pairs
        )
        if not has_pair:
            self.errors['invalid_pairs'] = 'Request should have at least ' \
                                           'one non-empty pair: {}'.format(self.pairs)


class ClientsInterestsRequestHandler(object):
    """
    Clients interests request handler
    """
    request_class = ClientsInterestsRequest

    def get_response(self, request, store, context):
        """
        Return user's interests for selected ids
        """
        r = self.request_class(request.arguments)
        if not r.is_valid():
            return r.format_errors(), INVALID_REQUEST

        context['nclients'] = len(r.client_ids)
        interests = {cid: get_interests(store, cid) for cid in r.client_ids}
        return interests, OK


class OnlineScoreRequestHandler(object):
    """
    Online scoring request handler
    """
    request_class = OnlineScoreRequest

    def get_response(self, request, store, context):
        """
        Return user's score based on given user fields
        """
        r = self.request_class(request.arguments)
        if not r.is_valid():
            return r.format_errors(), INVALID_REQUEST

        context['has'] = [
            name for name in r.fields.keys()
            if not r.is_empty(name)
        ]
        if request.is_admin:
            score = 42
        else:
            score = get_score(store, r.phone, r.email, r.birthday, r.gender, r.first_name,
                              r.last_name)
        return {'score': score}, OK


class MethodRequest(RequestBase):
    """
    Top-level request handler
    """
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        """
        Check if current user is administrator

        Returns:
            bool: True if current user is administrator
        """
        return self.login == ADMIN_LOGIN


def check_auth(request):
    """
    Check user token

    Returns:
        bool: True if current user token is valid
    """
    if request.is_admin:
        secret = datetime.now().strftime('%Y%m%d%H') + ADMIN_SALT
    else:
        secret = request.account + str(request.login) + SALT

    digest = hashlib.sha512(secret.encode()).hexdigest()
    return digest == request.token


def method_handler(request, ctx, store):
    """
    Process and validate requests
    """
    handlers = {
        'online_score': OnlineScoreRequestHandler,
        'clients_interests': ClientsInterestsRequestHandler,
    }

    method_request = MethodRequest(request['body'])
    if not method_request.is_valid():
        return method_request.format_errors(), INVALID_REQUEST
    if method_request.method not in handlers:
        return ERRORS[NOT_FOUND], NOT_FOUND
    if not check_auth(method_request):
        return ERRORS[FORBIDDEN], FORBIDDEN

    handler = handlers[method_request.method]()
    return handler.get_response(method_request, store, ctx)


class MainHTTPHandler(BaseHTTPRequestHandler):
    """
    HTTP Server for processing POST requests
    """
    router = {
        'method': method_handler
    }
    store = Store(RedisStorage(host=os.getenv('REDIS_HOST', 'localhost'),
                               port=int(os.getenv('REDIS_PORT', '6379'))))

    @staticmethod
    def get_request_id(headers):
        """
        Extract ID from request headers
        """
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        """
        Handle POST request
        """
        response, code = {}, OK
        context = {'request_id': self.get_request_id(self.headers)}
        request = None

        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception:
            data_string = None
            code = BAD_REQUEST

        if request:
            path = self.path.strip('/')
            logging.info('{}: {} {}'.format(self.path, data_string, context['request_id']))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {'body': request, 'headers': self.headers},
                        context,
                        self.store
                    )
                except Exception as e:
                    logging.exception('Unexpected error: {}'.format(e))
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if code not in ERRORS:
            r = {'response': response, 'code': code}
        else:
            r = {'error': response or ERRORS.get(code, 'Unknown Error'), 'code': code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode())
        return


if __name__ == '__main__':
    op = OptionParser(description='Scoring API')
    op.add_option('-p', '--port', action='store', type=int, default=8080, help='Port binding')
    op.add_option('-l', '--log', action='store', default=None, help='Log file path')
    opts, args = op.parse_args()
    logging.basicConfig(filename=opts.log,
                        level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(('localhost', opts.port), MainHTTPHandler)
    logging.info('Starting server at {}'.format(opts.port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
