from . import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


# for the relationship between project and user
rel_project_users = db.Table(
    'rel_project_users',
    db.Column('project_id', db.String(48), db.ForeignKey('projects.project_id'), primary_key=True),
    db.Column('uid', db.String(48), db.ForeignKey('users.uid'), primary_key=True)
)


class User(db.Model):
    """Data model for users
    """
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    uid = db.Column(db.String(64), primary_key=True, nullable=False)
    password = db.Column(db.String(128), index=False)
    first_name = db.Column(db.String(45), index=False)
    last_name = db.Column(db.String(45), index=False)
    role = db.Column(db.String(16), index=False)
    is_deleted = db.Column(db.String(8), index=False)

    def __repr__(self):
        return '<User {}>'.format(self.uid)

    # for Flask-Login
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.uid

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # for data API
    def as_dict(self):
        return {
            'uid': self.uid,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role
        }


class Admin(db.Model):
    """Data model for admins
    """
    __tablename__ = 'admins'
    __table_args__ = {'extend_existing': True}

    uid = db.Column(db.String(64), primary_key=True, nullable=False)
    password = db.Column(db.String(128), index=False)
    first_name = db.Column(db.String(45), index=False)
    last_name = db.Column(db.String(45), index=False)
    role = db.Column(db.String(16), index=False)

    def __repr__(self):
        return '<Admin {}>'.format(self.uid)


class Project(db.Model):
    """Data model for projects
    """
    __tablename__ = 'projects'
    __table_args__ = {'extend_existing': True}

    project_id = db.Column(db.String(48), primary_key=True, nullable=False)
    keystr = db.Column(db.String(64), unique=True)
    owner_uid = db.Column(db.String(64), index=False)
    title = db.Column(db.Text, index=False)
    abstract = db.Column(db.Text, index=False)
    date_created = db.Column(db.DateTime, index=False)
    date_updated = db.Column(db.DateTime, index=False)
    settings = db.Column(db.JSON, index=False)
    is_deleted = db.Column(db.String(8), index=False)
    
    # for the users
    users = db.relationship('User', secondary=rel_project_users, lazy='subquery',
        backref=db.backref('projects', lazy=True))

    # for JSON
    def as_dict(self):
        return {
            'project_id': self.project_id,
            'keystr': self.keystr,
            'owner_uid': self.owner_uid,
            'title': self.title,
            'abstract': self.abstract,
            'date_created': self.date_created,
            'date_updated': self.date_updated,
            'settings': self.settings,
            'users': [ u.as_dict() for u in self.users ]
        }

    def __repr__(self):
        return '<Project {0}: {1}>'.format(self.project_id, self.title)


class Paper(db.Model):
    """Data model for papers
    """
    __tablename__ = 'papers'
    __table_args__ = {'extend_existing': True}

    paper_id = db.Column(db.String(48), primary_key=True, nullable=False)
    pid = db.Column(db.String(64), index=False)
    pid_type = db.Column(db.String(8), index=False)
    project_id = db.Column(db.String(48), index=False)
    title = db.Column(db.Text, index=False)
    abstract = db.Column(db.Text, index=False)
    pub_date = db.Column(db.String(32), index=False)
    authors = db.Column(db.Text, index=False)
    journal = db.Column(db.String(128), index=False)
    meta = db.Column(db.JSON, index=False)
    ss_st = db.Column(db.String(8), index=False)
    ss_pr = db.Column(db.String(8), index=False)
    ss_rs = db.Column(db.String(8), index=False)
    date_created = db.Column(db.DateTime, index=False)
    date_updated = db.Column(db.DateTime, index=False)
    is_deleted = db.Column(db.String(8), index=False)

    def as_dict(self):
        # return {
        #     'paper_id': self.paper_id,
        #     'pid': self.pid,
        #     'pid_type': self.pid_type,
        #     'project_id': self.project_id,
        #     'title': self.title,
        #     'abstract': self.abstract,
        #     'pub_date': self.pub_date,
        #     'authors': self.authors,
        #     'journal': self.journal,
        #     'meta': self.meta,
        #     'ss_st': self.ss_st,
        #     'ss_pr': self.ss_pr,
        #     'ss_rs': self.ss_rs,
        #     'date_created': self.date_created,
        #     'date_updated': self.date_updated,
        # }
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<Paper {0}: {1} {2}>'.format(self.paper_id, self.pub_date, self.title)


class Note(db.Model):
    """Data model for notes
    """
    __tablename__ = 'notes'
    __table_args__ = {'extend_existing': True}

    note_id = db.Column(db.String(48), primary_key=True, nullable=False)
    paper_id = db.Column(db.String(48), index=False)
    project_id = db.Column(db.String(48), index=False)
    data = db.Column(db.JSON, index=False)
    date_created = db.Column(db.DateTime, index=False)
    date_updated = db.Column(db.DateTime, index=False)
    is_deleted = db.Column(db.String(8), index=False)

    def __repr__(self):
        return '<Note {0}: {1}>'.format(self.note_id, self.date_created)
