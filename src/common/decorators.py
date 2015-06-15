import traceback
from functools import wraps

def exc_handler(_function):
    @wraps(_function)
    def function_(*args,**kwargs):
        try:
            func = _function(*args,**kwargs)
            return func
        except Exception as msg:
            traceback.print_exc()
    return function_
