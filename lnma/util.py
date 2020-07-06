import json
import requests

from sqlalchemy.ext.declarative import DeclarativeMeta

class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


def is_valid_pmid(pmid):
    '''Check if a pmid is valid PMID

    Just a basic check
    '''
    # TODO implement this
    return True


def allowed_file_format(fn, exts=['csv', 'xls', 'xlsx']):
    return '.' in fn and \
        fn.rsplit('.', 1)[1].lower() in exts


# PubMed related functions
PUBMED_URL = {
    'base': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
    'esearch': 'esearch.fcgi?db={db}&term={term}&retmode=json',
    'esummary': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db={db}&id={ids}&retmode=json',
    'efetch': "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db={db}&id={uid}&retmode={retmote}&retype={retype}",
}

def _get_search_url(term, db='pubmed'):
    url = PUBMED_URL['base'] + PUBMED_URL['esearch'].format(db=db, term=term)
    return url


def _get_summary_url(ids, db='pubmed'):
    url = PUBMED_URL['base'] + PUBMED_URL['esummary'].format(db=db, ids=ids)
    return url


def _get_fetch_url(uid, db='pubmed', retmode='json', retype='abstract'):
    url = PUBMED_URL['base'] + PUBMED_URL['efetch'].format(db=db, uid=uid, retmode=retmode, retype=retype)
    return url


def e_search(term, db='pubmed'):
    '''search for term in pubmed
    '''
    url = _get_search_url(term)
    r = requests.get(url)
    if r.status_code != 200:
        print('* something wrong: {0}'.format(r.status_code))
        return None
    return r.json()


def e_summary(ids, db='pubmed'):
    '''get summary of pmid list
    '''
    url = _get_summary_url(','.join(ids))
    r = requests.get(url)
    if r.status_code != 200:
        print('* something wrong: {0}'.format(r.status_code))
        return None
    return r.json()


def e_fetch(ids, db='pubmed'):
    '''get ?
    '''
    url = _get_fetch_url(','.join(ids))
    r = requests.get(url)
    if r.status_code != 200:
        print('* something wrong: {0}'.format(r.status_code))
        return None
    return r.json()