#%% define packages and methods
import re
import json
import time
import datetime
import requests

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from sqlalchemy.ext.declarative import DeclarativeMeta

import logging
from pprint import pprint
logger = logging.getLogger("lnma.util")
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s')


# PubMed related functions
PUBMED_URL = {
    'base': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/',
    'esearch': 'esearch.fcgi?db={db}&term={term}&retmode=json&retmax={retmax}',
    'esummary': 'esummary.fcgi?db={db}&id={ids}&retmode=json',
    'efetch': "efetch.fcgi?db={db}&id={uid}&retmode={retmode}",
}


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


def _get_e_search_url(term, db='pubmed', retmax=300):
    url = PUBMED_URL['base'] + PUBMED_URL['esearch'].format(db=db, term=term, retmax=retmax)
    return url


def _get_e_summary_url(ids, db='pubmed'):
    url = PUBMED_URL['base'] + PUBMED_URL['esummary'].format(db=db, ids=ids)
    return url


def _get_e_fetch_url(uid, db='pubmed', retmode='xml'):
    url = PUBMED_URL['base'] + PUBMED_URL['efetch'].format(db=db, uid=uid, retmode=retmode)
    return url


def e_search(term, db='pubmed'):
    '''search for term in pubmed
    '''
    try_times = 0

    while True:
        url = _get_e_search_url(term)
        print('* e_search %s' % url)
        r = requests.get(url)

        if r.status_code == 200:
            return r.json()

        # something wrong?
        try_times += 1
        print('* Something wrong, HTTP Status Code: {0}'.format(r.status_code))
        if r.status_code == 429:
            print('* Reached MAX request limit of PubMed')

        if try_times < 3:
            dur = 7 * try_times
            print('* Wait for %s seconds and try again ...' % dur)
            time.sleep(dur)
        else:
            break
    
    print('* Tried e_search %s times but still failed ...' % try_times)
    return None


def e_summary(ids, db='pubmed'):
    '''get summary of pmid list
    '''
    try_times = 0

    while True:
        url = _get_e_summary_url(','.join(ids))
        print('* e_summary %s' % url)
        r = requests.get(url)

        if r.status_code == 200:
            return r.json()

        # something wrong?
        try_times += 1
        print('* Something wrong, HTTP Status Code: {0}'.format(r.status_code))
        if r.status_code == 429:
            print('* Reached MAX request limit of PubMed')

        if try_times < 3:
            dur = 7 * try_times
            print('* Wait for %s seconds and try again ...' % dur)
            time.sleep(dur)
        else:
            break
    
    print('* Tried e_summary %s times but still failed ...' % try_times)
    return None

    
def _e_fetch(ids, db='pubmed'):
    '''get the raw xml data from pubmed
    '''
    try_times = 0

    while True:
        url = _get_e_fetch_url(','.join(ids))
        print('* e_fetch %s' % url)
        r = requests.get(url)

        if r.status_code == 200:
            return r.text

        # something wrong?
        try_times += 1
        print('* Something wrong, HTTP Status Code: {0}'.format(r.status_code))
        if r.status_code == 429:
            print('* Reached MAX request limit of PubMed')

        if try_times < 3:
            dur = 7 * try_times
            print('* Wait for %s seconds and try again ...' % dur)
            time.sleep(dur)
        else:
            break
    
    print('* Tried e_fetch %s times but still failed ...' % try_times)
    return None


def e_fetch(ids, db='pubmed'):
    '''get jsonfied data
    '''
    text = _e_fetch(ids, db)

    if text is None:
        return None

    # parse the xml tree
    root = ET.fromstring(text)

    ret = {
        'result': {
            'uids': []
        }
    }
    for item in root.findall('PubmedArticle'):
        # check each item
        paper = {
            'uid': '',
            'sortpubdate': [],
            'source': '',
            'title': '',
            'authors': [],
            'abstract': []
        }

        # check each xml node
        for node in item.iter():
            if node.tag == 'PMID': 
                if paper['uid'] == '':
                    paper['uid'] = node.text
                else:
                    # other PMIDs will also appear in result
                    pass

            elif node.tag == 'ArticleTitle':
                paper['title'] = node.text

            elif node.tag == 'Abstract':
                for c in node:
                    if c is None or c.text is None:
                        pass
                    else:
                        paper['abstract'].append(c.text)

            elif node.tag == 'ISOAbbreviation':
                paper['source'] = node.text

            elif node.tag == 'DateRevised':
                for c in node:
                    paper['sortpubdate'].append(c.text)
                
            elif node.tag == 'AuthorList':
                for c in node:
                    fore_name = c.find('ForeName')
                    last_name = c.find('LastName')
                    name = ('' if fore_name is None else fore_name.text) + ' ' + \
                           ('' if last_name is None else last_name.text)

                    paper['authors'].append({
                        'name': name,
                        'authtype': 'Author'
                    })
        # merge abstract
        paper['abstract'] = ' '.join(paper['abstract'])
        paper['sortpubdate'] = '-'.join(paper['sortpubdate'])

        # append to return
        if paper['uid'] != '':
            ret['result']['uids'].append(paper['uid'])
            ret['result'][paper['uid']] = paper

    return ret


def parse_endnote_exported_xml(full_fn):
    '''Parse the file from endnote export
    '''
    try:
        tree = ET.parse(full_fn)
        root = tree.getroot()
    except Exception as err:
        logger.error('ERROR when parsing %s, %s' % (full_fn, err))
        return None

    papers = []
    for record in root.find('records').findall('record'):
        paper = {
            'pid': '',
            'pid_type': '',
            'title': '',
            'authors': '',
            'abstract': '',
            'pub_date': '',
            'pub_type': '',
            'journal': '',
        }

        for node in record.iter():
            if node.tag == 'F':
                c = node.attrib['C']

                if c == 'UI':
                    # update the pid
                    paper['pid'] = paper['pid'] if node.find('D') is None else node.find('D').text 
                elif c == 'ST':
                    # update the title
                    paper['pid_type'] = paper['pid_type'] if node.find('D') is None else node.find('D').text
                elif c == 'TI':
                    # update the title
                    paper['title'] = paper['title'] if node.find('D') is None else node.find('D').text
                elif c == 'AU':
                    # update the authors
                    paper['authors'] = ', '.join([ _.text for _ in node.findall('D') ])
                elif c == 'AB':
                    # update the abstract
                    paper['abstract'] = paper['abstract'] if node.find('D') is None else node.find('D').text
                elif c == 'SO':
                    # update the journal
                    paper['journal'] = paper['journal'] if node.find('D') is None else node.find('D').text
                elif c == 'YR':
                    # update the pub_date
                    paper['pub_date'] = paper['pub_date'] if node.find('D') is None else node.find('D').text
                elif c == 'PT':
                    # update the pub_type
                    paper['pub_type'] = paper['pub_type'] if node.find('D') is None else node.find('D').text
                else:
                    pass
        
        papers.append(paper)

    return papers


def pred_rct(ti, ab):
    '''Predict if a study is RCT
    '''
    url = 'http://localhost:12580/'
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {'ti': ti, 'ab': ab}
    data_str = json.dumps(data)
    r = requests.post(url, data=data_str, headers=headers)
    j = r.json()
    return j


def get_today_date_str():
    '''Get the today date string
    '''
    return datetime.datetime.today().strftime('%Y-%m-%d')


if __name__ == "__main__":
    papers = parse_endnote_exported_xml('/home/hehuan/Downloads/cites.xml')
    pprint(papers)