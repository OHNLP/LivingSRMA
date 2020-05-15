from flask import Blueprint

from flask_login import login_required
from flask_login import current_user


bp = Blueprint("user_portal", __name__, url_prefix="/user_portal")


@bp.route('/')
@login_required
def index():
    return 'User Portal' + ' | Logged in as: ' + current_user.uid