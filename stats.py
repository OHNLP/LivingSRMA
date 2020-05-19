#%% load packages and env
from lnma import db, create_app
from lnma.models import *
from lnma import dora

app = create_app()
db.init_app(app)
app.app_context().push()

#%% try simple count
n_users = User.query.count()
print('* Number of users: {:,}'.format(n_users))

n_projects = Project.query.count()
print('* Number of projects: {:,}'.format(n_projects))


# %% 
projects = Project.query.filter(Project.users.any(uid='hehuan2112@gmail.com')).all()
print(projects)