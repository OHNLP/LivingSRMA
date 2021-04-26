'''
For fixing the webfonts requests
'''
import functools
from flask import Blueprint

bp = Blueprint("webfonts", __name__, url_prefix="/webfonts")


@bp.route('/<fn>')
def index(fn):
    return ""
