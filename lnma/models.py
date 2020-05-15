from . import db

class User(db.model):
    """Data model for users
    """
    __tablename__ = 'users'

    uid = db.Column(db.String(64), primary_key=True)
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


class Admin(db.model):
    """Data model for admins
    """
    __tablename__ = 'admins'

    uid = db.Column(db.String(64), primary_key=True)
    password = db.Column(db.String(128), index=False)
    first_name = db.Column(db.String(45), index=False)
    last_name = db.Column(db.String(45), index=False)
    role = db.Column(db.String(16), index=False)

    def __repr__(self):
        return '<Admin {}>'.format(self.uid)


class Project(db.model):
    """Data model for projects
    """
    __tablename__ = 'projects'

    project_id = db.Column(db.Integer, primary_key=True)
    owner_uid = db.Column(db.String(64), index=False)
    title = db.Column(db.Text, index=False)
    abstract = db.Column(db.Text, index=False)
    date_created = db.Column(db.Datetime, index=False)
    date_updated = db.Column(db.Datetime, index=False)
    settings = db.Column(db.JSON, index=False)
    is_deleted = db.Column(db.String(8), index=False)

    def __repr__(self):
        return '<Project {0}:{1}>'.format(self.project_id, self.title)


class Paper(db.model):
    """Data model for papers
    """
    __tablename__ = 'papers'

    pid = db.Column(db.String(64), primary_key=True)
    pid_type = db.Column(db.String(8), index=False)
    project_id = db.Column(db.Integer, index=False)
    title = db.Column(db.String(256), index=False)
    pub_date = db.Column(db.String(32), index=False)
    authors = db.Column(db.Text, index=False)
    journal = db.Column(db.String(128), index=False)
    ss_states = db.Column(db.JSON, index=False)
    date_created = db.Column(db.Datetime, index=False)
    date_updated = db.Column(db.Datetime, index=False)
    is_deleted = db.Column(db.String(8), index=False)

    def __repr__(self):
        return '<Paper {0}:{1} {2}>'.format(self.pid, self.pub_date, self.title)