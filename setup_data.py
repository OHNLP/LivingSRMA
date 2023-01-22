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
    ['hehuan2112@gmail.com', 'LNMA2020', 'Huan', 'He', 'user,admin', 'no'],
    ['sipra.irbaz@gmail.com', 'LNMA2020', 'Irbaz', 'Riaz', 'user,admin', 'no'],
    ['arsalannaqvi016@gmail.com', 'LNMA2020', 'Arsalan', 'Naqvi', 'user', 'no'],
    ['rabbiasiddiqi@hotmail.com', 'LNMA2020', 'Rabbia', 'Siddiqi', 'user', 'no'],
]

projects = [
    ['sipra.irbaz@gmail.com', 'Cancer Associated Thrombosis', 'CAT', 'Cancer Associated Thrombosis'],
    ['sipra.irbaz@gmail.com', 'Metastatic Renal Cell Cancer', 'RCC', 'Metastatic Renal Cell Cancer'],
    ['sipra.irbaz@gmail.com', 'Toxicity of Immune Checkpoint Inhibitors 3', 'IO', 'IO Toxicity'],
    ['sipra.irbaz@gmail.com', 'Living Bladder Review', 'LBR', 'Living Bladder Review'],
]

# %% create users
def init_user(users):
    for r in users:
        is_existed, user = dora.create_user_if_not_exist(
            r[0], r[2], r[3], r[1], r[4]
        )
        if is_existed:
            print('* existed user [%s] %s %s' % (
                user.uid, user.first_name, user.last_name
            ))
        else:
            print('* add user [%s] ' % user.uid)

    print('* done user creation')
    return users


#%% create projects
def init_projects(projects, users):
    for r in projects:
        p, msg = dora.create_project(
            r[0], r[1], r[2], r[3]
        )

        if p is None:
            print('* existed project [%s]' % r[1])
        else:
            print('* created project [%s]' % r[1])
        
        for u in users:
            is_in, user, project = dora.add_user_to_project_by_keystr_if_not_in(
                u[0], r[2]
            )

            if is_in:
                print('* existed user [%s] in project [%s]' % (
                    u[0], r[1]
                ))
            else:
                print('* added user [%s] to project [%s]' % (
                    u[0], project.keystr
                ))

    print('* done setup data!')


#%% create table
def create_tables():
    # create the tables
    Piece.__table__.create(db.engine)
    print('* created table Piece')