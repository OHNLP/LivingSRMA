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

users = [
    ['hehuan2112@gmail.com', 'Mayo1234', 'Huan', 'He', 'user,admin', 'no'],
    ['sipra.irbaz@gmail.com', 'Mayo1234', 'Irbaz', 'Riaz', 'user,admin', 'no'],
    ['arsalannaqvi016@gmail.com', 'arsalannaqvi016', 'Arsalan', 'Naqvi', 'user', 'no'],
    ['rabbiasiddiqi@hotmail.com', 'rabbiasiddiqi', 'Rabbia', 'Siddiqi', 'user', 'no'],
]

# %% create users
if n_users == 0:
    # create the following
    for r in users:
        user = User(
            uid=r[0],
            password="",
            first_name=r[2],
            last_name=r[3],
            role=r[4],
            is_deleted=r[5]
        )
        user.set_password(r[1])
        db.session.add(user)
        print('* add user [%s]' % user.uid)

    db.session.commit()
    print('* created users')

else:
    print('* existed users, skip creation')


#%% create projects
if n_projects == 0:
    rs = [
        ['sipra.irbaz@gmail.com', 'Cancer Associated Thrombosis', 'CAT', 'Cancer Associated Thrombosis'],
        ['sipra.irbaz@gmail.com', 'Metastatic Renal Cell Cancer', 'RCC', 'Metastatic Renal Cell Cancer'],
        ['sipra.irbaz@gmail.com', 'LSR', 'LSR', 'LSR'],
    ]

    for r in rs:
        p = dora.create_project(
            r[0], r[1], r[2], r[3]
        )
        print('* created project [%s]' % r[1])
        
        for u in users:
            dora.add_user_to_project(u[0], p.project_id)
            print('* add [%s] to project [%s]' % (u[0], p.keystr))

else:
    print('* existed projects, skip creation')