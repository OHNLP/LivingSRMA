import enum
import json
from xml.sax.saxutils import escape

from . import db
from . import settings
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from sqlalchemy.dialects.mysql import LONGTEXT

from lnma import ss_state
from lnma import util
from lnma import settings

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


    def get_abbr(self):
        return "%s. %s" % (
            self.first_name[0].upper(), 
            self.last_name.upper()
        )


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


    def get_settings_text(self):
        '''
        Get all settings as a JSON string
        '''
        txt = json.dumps(self.settings, sort_keys=True, indent=4)
        return txt


    def get_cqs(self):
        '''
        Get clinical questions
        '''
        if 'clinical_questions' not in self.settings:
            return []

        else:
            return self.settings['clinical_questions']


    def get_cq_name(self, cq_abbr):
        '''
        Get the clinical question name by given abbr
        '''
        if 'clinical_questions' not in self.settings:
            return ''

        for cq in self.settings['clinical_questions']:
            if cq['abbr'] == cq_abbr:
                return cq['name']

        return ''


    def __repr__(self):
        return '<Project {0}: {1}>'.format(self.project_id, self.title)


class Paper(db.Model):
    """
    Data model for papers

    The `meta` could contain a lot of things:
    {
        all_rct_ids: Array(1)
        paper: Object
        pdfs: [{
            display_name: '',
            file_id: ''
            folder: ''
        }]
        pred: [{
            is_rct: true
            model: "svm_cnn_ptyp"
            preds: Object
            ptyp_rct: 0
            score: 3.472353767624721
            threshold_type: "balanced"
            threshold_value: 2.1057231048584675
        }]
        rct_id: "NCT01668784"
        rct_seq: 1
        study_type: "followup"
        tags: ['tag',]
    }

    The `ss_ex` could also contain a lot:
    {
        label: {
            CKL: { name: 'CKL' }
        },
        date_decided: "2021-03-27",
        decision: "included_sr",
        reason: "Through Abstract",
        ss_cq: {
            default: 'no'
        }
    }
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


    def get_ss_stages(self):
        '''
        Get the screen status stages of this paper
        '''
        stages = []

        if self.ss_pr == ss_state.SS_PR_NA and \
            self.ss_rs == ss_state.SS_RS_NA:
            stages.append(ss_state.SS_STAGE_UNSCREENED)

        if self.ss_pr != ss_state.SS_PR_NA or \
            self.ss_rs != ss_state.SS_RS_NA:
            stages.append(ss_state.SS_STAGE_DECIDED)

        if self.ss_rs == ss_state.SS_RS_EXCLUDED_TITLE:
            stages.append(ss_state.SS_STAGE_EXCLUDED_BY_TITLE)

        if self.ss_rs == ss_state.SS_RS_EXCLUDED_ABSTRACT:
            stages.append(ss_state.SS_STAGE_EXCLUDED_BY_ABSTRACT)

        if self.ss_rs == ss_state.SS_RS_EXCLUDED_FULLTEXT:
            stages.append(ss_state.SS_STAGE_EXCLUDED_BY_FULLTEXT)

        if self.ss_rs == ss_state.SS_RS_INCLUDED_ONLY_SR:
            stages.append(ss_state.SS_STAGE_INCLUDED_ONLY_SR)
            stages.append(ss_state.SS_STAGE_INCLUDED_SR)

        if self.ss_rs == ss_state.SS_RS_INCLUDED_SRMA:
            stages.append(ss_state.SS_STAGE_INCLUDED_SRMA)
            stages.append(ss_state.SS_STAGE_INCLUDED_SR)

        return stages


    def is_ss_included_in_project(self):
        '''
        Check whether this paper is included in project
        '''
        if self.ss_rs in [
            ss_state.SS_RS_INCLUDED_ONLY_SR,
            ss_state.SS_RS_INCLUDED_ONLY_MA,
            ss_state.SS_RS_INCLUDED_SRMA
        ]:
            return True

        else:
            return False


    def get_rct_id(self):
        '''
        Get the RCT ID (NCT) or other number
        '''
        if 'rct_id' in self.meta:
            return self.meta['rct_id']
        else:
            return ''


    def get_study_type(self):
        '''
        Get the study type (original / follow-up)
        '''
        if 'study_type' in self.meta:
            return self.meta['study_type']
        else:
            return ''


    def get_short_name(self, style=None):
        '''
        Get a short name for this study

        For example,

        He et al 2021
        Huan He et al 2021

        '''
        year = util.get_year(self.pub_date)
        fau_etal = util.get_author_etal_from_authors(self.authors)

        return '%s %s' % (fau_etal, year)


    def get_year(self):
        '''
        Get the year from this record
        '''
        return util.get_year(self.pub_date)

    
    def update_ss_cq_by_cqs(self, cqs, 
        decision=settings.SCREENER_DEFAULT_DECISION_FOR_CQ_INCLUSION):
        '''
        Update the ss_cq in the ss_ex

        This attiribute is used only for those included studies.
        '''
        if self.is_ss_included_in_project():
            # ok, let's check the cq
            if 'ss_cq' in self.ss_ex:
                pass
            else:
                self.ss_ex['ss_cq'] = {}
            
            # check each cq
            if len(cqs) == 1:
                # if there is only one cq, just set to yes
                decision = util.make_ss_cq_decision(
                    settings.PAPER_SS_EX_SS_CQ_YES,
                    '',
                    'yes'
                )

            for cq in cqs:
                if cq['abbr'] in self.ss_ex['ss_cq']:
                    # update the format
                    if (type(self.ss_ex['ss_cq'][cq['abbr']]) == str):
                        # oh, it's not the format we need now
                        # str format yes/no is the old format for cq
                        # we need a dict format to put more information
                        self.ss_ex['ss_cq'][cq['abbr']] = util.make_ss_cq_decision(
                            self.ss_ex['ss_cq'][cq['abbr']],
                            '',
                            'no'
                        )
                    else:
                        # great! we already have this cq set in dict format
                        if 'c' in self.ss_ex['ss_cq'][cq['abbr']]:
                            pass
                        else:
                            self.ss_ex['ss_cq'][cq['abbr']]['c'] = 'no'
                else:
                    # nice! just add this lovely new cq
                    self.ss_ex['ss_cq'][cq['abbr']] = util.make_ss_cq_decision(
                        decision,
                        '',
                        'no'
                    )
        else:
            # ok, this study is not included in SR
            # so ... no need to add this ss_cq
            pass

        # ok, that's all

    def get_simple_pid_type(self):
        '''
        Get the simple pid type
        '''
        pid_type = self.pid_type.upper()

        if 'OVID' in pid_type or \
            'MEDLINE' in pid_type:
            return 'MEDLINE'
        if 'PMID' in pid_type or \
            'PUBMED' in pid_type:
            return 'PUBMED'
        if 'EMBASE' in pid_type:
            return 'EBASE'

        return pid_type

    
    def is_pmid(self):
        '''
        Get the flag of is pmid

        We could use pmid for a lot of things
        '''
        pid_type = self.pid_type.upper()

        if 'OVID' in pid_type or \
            'MEDLINE' in pid_type or \
            'PMID' in pid_type or \
            'NLM' in pid_type or \
            'PUBMED' in pid_type:

            if util.is_valid_pmid(self.pid):
                return True
            else:
                return False

        return False
        

    def as_dict(self):
        # convert all basic attributes
        ret = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        # add other values that not directly converted
        ret['is_pmid'] = self.is_pmid()
        ret['year'] = self.get_year()
        ret['rct_id'] = self.get_rct_id()
        ret['short_name'] = self.get_short_name()
        ret['study_type'] = self.get_study_type()

        return ret

    
    def as_simple_dict(self):
        '''
        Return the simple data of this paper

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
        '''
        Return the simple data of this paper

        Reduce the object size by remove the abstract
        '''
        simple_dict = self.as_simple_dict()
        simple_dict['abstract'] = ''
        simple_dict['authors'] = ''
        simple_dict['date_created'] = self.date_created.strftime('%Y-%m-%d')
        simple_dict['pid_type'] = self.get_simple_pid_type()

        # delete those for import information
        if 'xml' in simple_dict['meta']: del simple_dict['meta']['xml']
        if 'raw_type' in simple_dict['meta']: del simple_dict['meta']['raw_type']
        
        del simple_dict['is_deleted']
        del simple_dict['project_id']

        return simple_dict

    
    def as_quite_simple_dict(self):
        '''
        Return the very very simple data of this paper
        '''
        d = self.as_simple_dict()
        del d['paper_id']
        del d['pid_type']
        del d['date_updated']

        # delete those for import information
        if 'xml' in d['meta']: del d['meta']['xml']
        if 'raw_type' in d['meta']: del d['meta']['raw_type']

        return d


    def as_endnote_xml(self):
        '''
        Return the EndNote XML format fragment
        '''
        if 'raw_type' in self.meta and self.meta['raw_type'] == 'endnote_xml':
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


    def from_pubmed_record(self, pubmed_record):
        '''
        Update this item from a pubmed record
        '''
        self.title = pubmed_record['title']
        self.abstract = pubmed_record['abstract']
        self.pub_date = pubmed_record['sortpubdate']
        self.authors = ', '.join([ a['name'] for a in pubmed_record['authors'] ])
        self.journal = pubmed_record['source']


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
        cq_abbr: 'IMM',       # for clinical question
        oc_type: 'pwma',
        group: 'Primary',
        category: 'default',
        full_name: 'pwma Outcome full name',

        # for subg
        "is_subg_analysis": 'no',
        "sub_groups": ['A', 'B'],
        
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

    The `data` attribute contains all the extraction results.
    It's a pid based (e.g., PMID) dictionary.
    {
        pid: {
            is_selected: true / false,
            is_checked: true / false,
            n_arms: 2 / 3 / 4 / 5,
            attrs: {
                main: {
                    g0: {  # the 0 is the default group
                        attr_sub_abbr: value
                    },
                    g1: {  # the 1 and others are other sub groups

                    }
                },
                other: [{
                    g0: {
                        attr_sub_abbr: value
                    },
                    g1: {

                    }
                }, ...]
            }
        }
    }
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


    def update_meta(self):
        '''
        Update / validate the meta according to default template by oc_type

        Fix the missing attributes in desing
        '''
        meta_template = settings.OC_TYPE_TPL[self.oc_type]['default']

        for attr_name in meta_template:
            if attr_name not in self.meta:
                self.meta[attr_name] = meta_template[attr_name]
                print(f'* fixed missing attr[{attr_name}] in meta')


    def update_data(self):
        '''
        Double check the current extract with its meta data
        '''
        pids = set([])

        # for pid in self.data:


    def update_data_by_papers(self, papers):
        '''
        Extend the current extract with more papers
        according to the given papers.
        And also update existing papers according the extract meta
        '''
        # merge the return obj
        # make a ref in the extract for frontend display
        # make sure every selected paper is listed in extract.data
        pids = set([])
        for paper in papers:
            pid = paper.pid
            # record this pid for next step
            pids.add(pid)

            # check if this pid exists in extract
            if pid in self.data:
                # nothing to do if has added
                # 2021-07-12: fix the sub group update
                # for those already existsed, the subgroup may updated
                for g_idx, g in enumerate(self.meta['sub_groups']):
                    # check the main
                    self.data[pid]['attrs']['main'] = util.fill_extract_data_arm(
                        self.data[pid]['attrs']['main'],
                        self.meta['cate_attrs'],
                        g_idx
                    )
                    # check the other arms
                    for idx in range(len(self.data[pid]['attrs']['other'])):
                        self.data[pid]['attrs']['other'][idx] = util.fill_extract_data_arm(
                            self.data[pid]['attrs']['other'][idx],
                            self.meta['cate_attrs'],
                            g_idx
                        )
                # after update the meta, we could skip this paper
                continue

            print('* NOT FOUND pid[%s] in this extract[%s]' % (
                pid,
                self.abbr
            ))
            # if not exist, add this paper
            self.data[pid] = {
                'is_selected': False,
                'is_checked': False,
                'n_arms': 2,
                'attrs': {}
            }

            self.data[pid]['attrs'] = {
                'main': {},
                'other': []
            }

            # fill the main track with empty values
            for g_idx, g in enumerate(self.meta['sub_groups']):
                self.data[pid]['attrs']['main'] = util.fill_extract_data_arm(
                    self.data[pid]['attrs']['main'],
                    self.meta['cate_attrs'],
                    g_idx
                )

        # reverse search, unselect those are not in papers
        for pid in self.data:
            if pid in pids:
                # which means this pid is in the SR stage
                continue

            # if not, just unselect this paper
            # don't delete
            self.data[pid]['selected'] = False

        # in fact, we don't need to return much things
        return pids


    def get_n_selected(self):
        '''
        Get the number of selected papers
        '''
        n = 0
        for pid in self.data:
            if self.data[pid]['is_selected']:
                n += 1

        return n

    
    def get_short_title(self):
        '''
        Get a short title for this extract
        '''
        return self.meta['full_name']


    def __repr__(self):
        return '<Extract {0} {1}: {2}>'.format(
            self.oc_type, self.abbr, self.extract_id)


    def as_dict(self):
        '''
        Return the dict format of this object
        '''
        ret = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        # add how many selected
        ret['n_selected'] = self.get_n_selected()

        return ret


    def as_simple_dict(self):
        '''
        Return the simple data of this extract

        Reduce the object size
        '''
        full_dict = self.as_dict()

        for attr in ['data', 'project_id', 'extract_id']:
            if attr in full_dict:
                del full_dict[attr]

        return full_dict


    def as_very_simple_dict(self):
        '''
        Return the very simple format
        '''
        simple_dict = self.as_simple_dict()

        if 'cate_attrs' in simple_dict['meta']:
            del simple_dict['meta']['cate_attrs']

        return simple_dict


class Piece(db.Model):
    """
    The extracted data piece details

    It uses three IDs to locate:

    1. project_id: decide which project is working on
    2. abbr: decide which extract is working on
    3. pid: decide which paper

    The piece contains the information related to an outcome (or AE).
    The `data` attribute contains all the extraction results.
    {
        is_selected: true / false,
        is_checked: true / false,
        n_arms: 2 / 3 / 4 / 5,
        attrs: {
            main: {
                attr_sub_abbr: value
            },
            other: [{
                attr_sub_abbr: value
            }, ...]
        }
    }
    """
    
    __tablename__ = 'pieces'
    __table_args__ = {'extend_existing': True}

    piece_id = db.Column(db.String(48), primary_key=True, nullable=False)
    project_id = db.Column(db.String(48), index=False)
    abbr = db.Column(db.String(48), index=False)
    pid = db.Column(db.String(settings.PAPER_PID_MAX_LENGTH), index=False)
    data = db.Column(db.JSON, index=False)
    date_created = db.Column(db.DateTime, index=False)
    date_updated = db.Column(db.DateTime, index=False)

    def __repr__(self):
        return '<Piece {0} in {1}: {2}>'.format(
            self.pid, self.abbr, self.piece_id)


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
