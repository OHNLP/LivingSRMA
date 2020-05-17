from lnma import db, create_app
from lnma.models import Admin, User, Project, Paper
from lnma import dora

app = create_app()
db.init_app(app)
app.app_context().push()

n_users = User.query.count()
print('* Number of users: {:,}'.format(n_users))

paper = dora.create_paper_by_pmid('123', '24019545')
print(paper)