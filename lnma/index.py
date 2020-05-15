from flask import Blueprint
from flask import render_template

from flask_login import login_required
from flask_login import current_user

from .models import Admin

bp = Blueprint("index", __name__, url_prefix="/")

@bp.route('/')
def index():
    rs = Admin.query.all()
    
    print(rs)
    return 'index'