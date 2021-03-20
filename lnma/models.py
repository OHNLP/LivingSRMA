from xml.sax.saxutils import escape

from . import db
from . import settings
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from sqlalchemy.dialects.mysql import LONGTEXT


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

    # for Flask-login
    def is_authenticated(self):
        return True

    def is_active(self):
        return self.is_deleted == 'no'

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.uid

    # for data API
    def as_dict(self):
        return {
            'uid': self.uid,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role
        }

    def set_password(self, raw_pass):
        self.password = generate_password_hash(raw_pass)

    def __repr__(self):
        return '<User {}>'.format(self.uid)


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
    related_users = db.relationship('User', secondary=rel_project_users, lazy='subquery',
        backref=db.backref('related_projects', lazy=True))

    # for JSON
    def as_dict(self):
        return {
            'project_id': self.project_id,
            'keystr': self.keystr,
            'owner_uid': self.owner_uid,
            'title': self.title,
            'abstract': self.abstract,
            'date_created': self.date_created.strftime('%Y-%m-%d'),
            'date_updated': self.date_updated.strftime('%Y-%m-%d'),
            'settings': self.settings,
            'related_users': [ u.as_dict() for u in self.related_users ]
        }


    def is_user_in(self, uid):
        for u in self.related_users:
            if u.uid == uid:
                return (True, u)
        return (False, None)


    def get_tags_text(self):
        '''
        Get the tags in plain text format
        '''
        if 'tags' in self.settings:
            txt = '\n'.join(self.settings['tags'])
        else:
            txt = ''

        return txt


    def get_inclusion_criterias_text(self):
        '''
        Get the inclusion criterias in plain text format
        '''
        txt = ''
        if 'criterias' in self.settings:
            if 'inclusion' in self.settings['criterias']:
                txt = self.settings['criterias']['inclusion']
        return txt
        

    def get_exclusion_criterias_text(self):
        '''
        Get the exclusion criterias in plain text format
        '''
        txt = ''
        if 'criterias' in self.settings:
            if 'exclusion' in self.settings['criterias']:
                txt = self.settings['criterias']['exclusion']
        return txt
        

    def get_exclusion_reasons_text(self):
        '''
        Get the exclusion reasons in plain text format
        '''
        txt = ''
        if 'exclusion_reasons' in self.settings:
            txt = '\n'.join(self.settings['exclusion_reasons'])
        return txt


    def get_inclusion_keywords_text(self):
        '''
        Get the inclusion keywords in plain text format
        '''
        txt = ''
        if 'highlight_keywords' in self.settings:
            if 'inclusion' in self.settings['highlight_keywords']:
                txt = '\n'.join(self.settings['highlight_keywords']['inclusion'])
        return txt


    def get_exclusion_keywords_text(self):
        '''
        Get the exclusion keywords in plain text format
        '''
        txt = ''
        if 'highlight_keywords' in self.settings:
            if 'exclusion' in self.settings['highlight_keywords']:
                txt = '\n'.join(self.settings['highlight_keywords']['exclusion'])
        return txt


    def get_pdf_keywords_text(self):
        '''
        Get the PDF keywords in plain text format
        '''
        txt = ''
        if 'pdf_keywords' in self.settings:
            if 'main' in self.settings['pdf_keywords']:
                txt = '\n'.join(self.settings['pdf_keywords']['main'])
        return txt


    def __repr__(self):
        return '<Project {0}: {1}>'.format(self.project_id, self.title)


class Paper(db.Model):
    """Data model for papers
    """
    __tablename__ = 'papers'
    __table_args__ = {'extend_existing': True}

    paper_id = db.Column(db.String(48), primary_key=True, nullable=False)
    pid = db.Column(db.String(settings.PAPER_PID_MAX_LENGTH), index=False)
    pid_type = db.Column(db.Text, index=False)
    seq_num = db.Column(db.Integer, index=False)
    project_id = db.Column(db.String(48), index=False)
    title = db.Column(db.Text, index=False)
    abstract = db.Column(LONGTEXT, index=False)
    pub_date = db.Column(db.String(settings.PAPER_PUB_DATE_MAX_LENGTH), index=False)
    authors = db.Column(db.Text, index=False)
    journal = db.Column(db.Text, index=False)
    meta = db.Column(db.JSON, index=False)
    ss_st = db.Column(db.String(8), index=False)
    ss_pr = db.Column(db.String(8), index=False)
    ss_rs = db.Column(db.String(8), index=False)
    ss_ex = db.Column(db.JSON, index=False)
    date_created = db.Column(db.DateTime, index=False)
    date_updated = db.Column(db.DateTime, index=False)
    is_deleted = db.Column(db.String(8), index=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    
    def as_simple_dict(self):
        '''Return the simple data of this paper

        Reduce the object size
        '''
        full_dict = self.as_dict()
        if 'paper' in full_dict['meta']:
            del full_dict['meta']['paper']

        if 'pred' in full_dict['meta']:
            is_rct = full_dict['meta']['pred'][0]['is_rct']
            usr_fb = full_dict['meta']['pred'][0].get('usr_fb', '')
            
            # remove other values, just keep the is_rct
            full_dict['meta']['pred'][0] = {
                'is_rct': is_rct,
                'usr_fb': usr_fb
            }

        # remove the abstract to reduce file size
        # this require the frontend to reload this paper information
        # full_dict['abstract'] = ''

        return full_dict


    def as_very_simple_dict(self):
        '''Return the simple data of this paper

        Reduce the object size by remove the abstract
        '''
        simple_dict = self.as_simple_dict()
        simple_dict['abstract'] = ''

        return simple_dict


    def as_endnote_xml(self):
        '''
        Return the EndNote XML format fragment
        '''
        if self.meta['raw_type'] == 'endnote_xml':
            # this paper is imported by endnote
            return self.meta['xml']
            
        author_list = self.authors.split(',')
        xml = """
<record>
    <database name="EndNote_Export.enl">EndNote_Export.enl</database>
    <source-app name="EndNote" version="19.3">EndNote</source-app>
    <contributors>
        <authors>
        {contributors}
        </authors>
    </contributors>
    <dates>
        <year>
            <style face="normal" font="default" size="100%">{year}</style>
        </year>
    </dates>
    <periodical>
        <full-title>
            <style face="normal" font="default" size="100%">{journal}</style>
        </full-title>
    </periodical>
    <accession-num>
        <style face="normal" font="default" size="100%">{accession_num}</style>
    </accession-num>
    <titles>
        <title>
            <style face="normal" font="default" size="100%">{title}</style>
        </title>
    </titles>
    <abstract>
        <style face="normal" font="default" size="100%">{abstract}</style>
    </abstract>
</record>
        """.format(
            contributors= "\n".join([ '<author>%s</author>' % escape(au) for au in author_list ]),
            accession_num=self.pid,
            title=escape(self.title),
            abstract=escape(self.abstract),
            year=escape(self.pub_date),
            journal=escape(self.journal)
        )
        return xml


    def as_ovid_xml(self):
        '''
        Return the OVID XML format fragment
        '''
        author_list = self.authors.split(',')
        xml = """
<record>
    <F C="UI" L="Unique Identifier">
        <D type="c">{UI}</D>
    </F>
    <F C="TI" L="Title">
        <D type="c">{TI}</D>
    </F>
    <F C="SO" L="Source">
        <D type="c">{SO}</D>
    </F>
    <F C="VI" L="Version ID">
        <D type="c">{VI}</D>
    </F>
    <F C="ST" L="Status">
        <D type="c">{ST}</D>
    </F>
    <F C="AU" L="Authors">
        {AU}
    </F>
    <F C="AB" L="Abstract">
        <D type="c">{AB}</D>
    </F>
    <F C="YR" L="Year of Publication">
        <D type="c">{YR}</D>
    </F>
</record>
        """.format(
            UI=self.pid,
            TI=escape(self.title),
            SO=escape(self.journal),
            VI=1,
            ST=escape(self.pid_type),
            AU="\n".join([ '<D type="s">%s</D>' % escape(au) for au in author_list ]),
            AB=escape(self.abstract),
            YR=escape(self.pub_date)
        )

        return xml


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


class DataSource(db.Model):
    """
    Data source for the studies, such as email, xml, and pmid list
    """
    __tablename__ = 'datasources'
    __table_args__ = {'extend_existing': True}

    datasource_id = db.Column(db.String(48), primary_key=True, nullable=False)
    ds_type = db.Column(db.String(48), index=False)
    title = db.Column(db.Text, index=False)
    content = db.Column(LONGTEXT, index=False)
    date_created = db.Column(db.DateTime, index=False)

    def __repr__(self):
        return '<DataSource {0}: {1}>'.format(self.ds_type, self.title)


class Extract(db.Model):
    """
    The product details extracted by user

    The extraction contains the information related to an outcome (or AE).
    The oc_type currently have the following:

    - pwma
    - subg
    - nma
    - itable

    For each oc_type, the meta content would be different accordingly.

    For the `pwma` type, the `meta` includes:
    {
        abbr: '',
        oc_type: 'pwma',
        category: 'default',
        group: 'Primary',
        full_name: 'pwma Outcome full name',
        included_in_plots: 'yes',
        included_in_sof: 'yes',
        input_format: 'PRIM_CAT_RAW',
        measure_of_effect: 'RR',
        fixed_or_random: 'fixed',
        which_is_better: 'lower',
        attrs: null,
        cate_attrs: null
    }

    Some attributes are designed for the public site only.
    More information would be added in the future.
    """
    
    __tablename__ = 'extracts'
    __table_args__ = {'extend_existing': True}

    extract_id = db.Column(db.String(48), primary_key=True, nullable=False)
    project_id = db.Column(db.String(48), index=False)
    oc_type = db.Column(db.String(48), index=False)
    abbr = db.Column(db.String(48), index=False)
    meta = db.Column(db.JSON, index=False)
    data = db.Column(db.JSON, index=False)
    date_created = db.Column(db.DateTime, index=False)
    date_updated = db.Column(db.DateTime, index=False)

    def __repr__(self):
        return '<Extract {0} {1}: {2}>'.format(
            self.oc_type, self.abbr, self.extract_id)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}