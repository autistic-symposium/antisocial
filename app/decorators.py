"""
    For cases when an entire function needs to be made available
    only to users with certain permissions, we create a custom
    decorator.
    Decorators are built with the help of functools package
"""

from functools import wraps
from flask import abort
from flask.ext.login import current_user
from .models import Permission


# decorator to check user permissions
# returning 402 when the current user doesn't have permission
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# decorator to checks for an admin permission
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
