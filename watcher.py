#%% load packages and env
import json
import requests

from lnma import db, create_app
from lnma.models import *
from lnma import dora

app = create_app()
db.init_app(app)
app.app_context().push()

#%% try simple count
n_users = User.query.count()
print('* Number of users: {:,}'.format(n_users))

URL = {
    'base': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
    'esearch': 'esearch.fcgi?db={db}&term={term}&retmode=json',
    'esummary': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db={db}&id={ids}&retmode=json',
    'efetch': "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db={db}&id={uid}&retmode={retmote}&retype={retype}",
}

def get_search_url(term, db='pubmed'):
    url = URL['base'] + URL['esearch'].format(db=db, term=term)
    return url


def get_summary_url(ids, db='pubmed'):
    url = URL['base'] + URL['esummary'].format(db=db, ids=ids)
    return url


def get_fetch_url(uid, db='pubmed', retmode='json', retype='abstract'):
    url = URL['base'] + URL['efetch'].format(db=db, uid=uid, retmode=retmode, retype=retype)
    return url


def search(term, db='pubmed'):
    '''search for term in pubmed
    '''
    url = get_search_url(term)
    r = requests.get(url)
    if r.status_code != 200:
        print('* something wrong: {0}'.format(r.status_code))
        return None
    return r.json()


#%% check updates

query = 'renal cell cancer AND "last 2 years"[Date - Create]'
j = search(query)

# %%
