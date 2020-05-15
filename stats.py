from lnma import db, create_app
from lnma.models import Admin, User, Project, Paper

app = create_app()
db.init_app(app)
app.app_context().push()

n_users = User.query.count()
print('* Number of users: {:,}'.format(n_users))