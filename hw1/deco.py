from functools import update_wrapper


def disable(func):
    """
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable
    """
    return func


def decorator(func):
    """
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    """
    def wrapper(d):
        return update_wrapper(func(d), d)
    return wrapper


@decorator
def countcalls(func):
    """
    Decorator that counts calls made to the function decorated.
    """
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


@decorator
def memo(func):
    """
    Memoize a function so that it caches all return values for faster future lookups.
    """
    cache = {}

    def wrapper(*args, **kwargs):
        update_wrapper(wrapper, func)
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper


@decorator
def n_ary(func):
    """
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y, z)), etc. Also allow f(x) = x.
    """
    def wrapper(x, *args):
        return x if not args else func(x, wrapper(*args))
    return wrapper


def trace(filler):
    """Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3
    """
    @decorator
    def dec(func):
        def wrapper(*args, **kwargs):
            indent = filler * wrapper.level
            arguments = ', '.join(str(x) for x in args)
            print('{} --> {}({})'.format(indent, func.__name__, arguments))
            wrapper.level += 1

            result = func(*args, **kwargs)
            print('{} <-- {}({}) == {}'.format(indent, func.__name__, arguments, result))
            wrapper.level -= 1
            return result
        wrapper.level = 0
        return wrapper
    return dec


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace('####')
@memo
def fib(n):
    """
    Some doc
    """
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print('===== foo =====')
    print(foo(4, 3))
    print(foo(4, 3, 2))
    print(foo(4, 3))
    print(foo.__name__, 'was called', foo.calls, 'times')

    print('===== bar =====')
    print(bar(4, 3))
    print(bar(4, 3, 2))
    print(bar(4, 3, 2, 1))
    print(bar.__name__, 'was called', bar.calls, 'times')

    print('===== fib =====')
    print(fib(3))
    print(fib.__name__, 'was called', fib.calls, 'times')
    print(fib.__doc__)


if __name__ == '__main__':
    main()
