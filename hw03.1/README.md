# Homework 03.1: Testing

## Scoring API

Testing of HTTP scoring service API.



### Request structure

```
{
    "account": "<partner company name>", 
    "login": "<user name>", 
    "method": "<method name>",
    "token": "<authentication token>", 
    "arguments": {
        <dictionary with method arguments>
    }
}
```

- `account` — string, optional, may be empty
- `login` — string, required, may be empty
- `method` — string, required, may be empty
- `token` — string, required, may be empty
- `arguments` — dictionary, required, may be empty



### Response structure

If success:

```
{
    "code": <response numeric code>,
    "response": {
        <method response data>
    },
}
```

If an error occurred:

```
{
    "code": <response numeric code>, 
    "error": {
        <error message>
    }
}
```



### Method `online_score`

**Arguments:**

- `phone` — string or number, 11 characters, starts with `7`, optional, may be empty
- `email` — string, contains `@`, optional, may be empty
- `first_name` — string, optional, may be empty
- `last_name` — string, optional, may be empty
- `birthday` — date `DD.MM.YYYY`, less than 70 years, optional, may be empty
- `gender` — number `0`, `1` or `2`, optional, may be empty

**Response structure:**

If success:

```
{
    "score": <number>
}
```

If request from valid user `admin`:

```
{
    "score": 42
}
```

If validation error:

```
{
    "code": 422,
    "error": "<invalid fields list>"
}
```

**Request example:**

```bash
curl -X POST -H "Content-Type: application/json" -d '{
	"account": "horns&hoofs",
	"login": "h&f",
	"method": "online_score",
	"token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
	"arguments": {
		"phone": "79175002040",
		"email": "stupnikov@otus.ru",
		"first_name": "Стансилав",
		"last_name": "Ступников",
		"birthday": "01.01.1990",
		"gender": 1
	}
}' http://127.0.0.1:8080/method/
# {"response": {"score": 5.0}, "code": 200} 
```



### Method `client_interests`

**Arguments:**

- `client_ids` — array or numbers, required, not empty
- `date` — date `DD.MM.YYYY`, optional, may be empty

**Response structure:**

If success:

```
{
    "client_id1": ["interest1", "interest2" ...],
    "client_id2": [...]
}
```

If validation error:

```
{
    "code": 422,
    "error": "<invalid fields list>"
}
```

**Request example:**

```bash
curl -X POST -H "Content-Type: application/json" -d '{
	"account": "horns&hoofs",
	"login": "admin",
	"method": "clients_interests",
	"token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95",
	"arguments": {
		"client_ids": [1,2,3,4],
		"date": "20.07.2017"
	}
}' http://127.0.0.1:8080/method/
# {"response": {"1": ["cinema", "travel"], "2": ["books", "cinema"], "3": ["otus", "geek"], "4": ["pets", "books"]}, "code": 200}
```



### Requirements

- Python 3.x
- Redis



### Install dependencies

```bash
pip3 install -r requirements.txt
```



### How to run

```bash
$ python3 api.py -h

Usage: api.py [options]

Scoring API

Options:
  -h, --help            show this help message and exit
  -p PORT, --port=PORT  Port binding
  -l LOG, --log=LOG     Log file path
```

Run in Docker:

```bash
docker-compose up -d --build
```



### Testing

```bash
python3 -m unittest
```
