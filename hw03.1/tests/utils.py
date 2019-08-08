import functools


def cases(test_cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for case_idx, case in enumerate(test_cases, 1):
                new_args = args + (case if isinstance(case, tuple) else (case,))
                try:
                    f(*new_args)
                except Exception as e:
                    message = '{} | Test: {} | Case {}: {}'.format(e, args[0], case_idx, repr(case))
                    raise type(e)(message) from e
        return wrapper
    return decorator
