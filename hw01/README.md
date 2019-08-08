# Homework 01: Advanced Basics

## Poker

Script for comparing "hands" in the "Poker" game.

### Requirements

- Python 3.x

### How to run

```bash
python3 poker.py
```



## Deco

Implementation of several decorators.

- `disable` — Disable a decorator by re-assigning the decorator's name to this function
- `decorator` — Decorate a decorator so that it inherits the docstrings and stuff from the function it's decorating
- `countcalls` — Decorator that counts calls made to the function decorated
- `memo` — Memoize a function so that it caches all return values for faster future lookups
- `n_ary` — Given binary function `f(x, y)`, return an n_ary function such that `f(x, y, z) = f(x, f(y, z))`
- `trace` — Trace calls made to function decorated.

### Requirements

- Python 3.x

### How to run

```bash
python3 deco.py
```



## Log Analyzer

Script for parsing and analyzing nginx logs.

Script should parse nginx logs in specified directory and generate report about time spent to process different HTTP requests.

### Requirements

- Python 3.x

### How to run

```bash
# Change current directory
cd log_analyzer

# Run script
python3 log_analyzer.py -h

usage: log_analyzer.py [-h] [-c CONFIG]

Log Analyzer

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to config file
```

### Testing

```bash
python3 tests.py
```