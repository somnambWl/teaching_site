from functools import wraps, update_wrapper
from flask import session, request, redirect, url_for, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            # when login, redirect again back to request.url
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_admin' in session and session['is_admin']:
            pass
        else:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def only_from(*args):
    def decorator(f):
        def decorated_function(*f_args, **f_kwargs):
            if 'is_admin' in session and session['is_admin']:
                pass
            else:
                origin = str(request.referrer).split('/')[-1]
                if origin not in args:
                    abort(403)
            return f(*f_args, **f_kwargs)
        return update_wrapper(decorated_function, f)
    return decorator
