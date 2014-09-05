"""
    Manage the Blueprint creation
"""

from flask import Blueprint

# the constructor has two arguments: the blueprint name and the
# module or package where the blueprint is located
main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
