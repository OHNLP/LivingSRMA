#%% define packages and methods
import os
import re
import json
import time
import random
import datetime
import requests

import uuid 

from werkzeug.utils import secure_filename

from tqdm import tqdm

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

from . import settings

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


def mk_oc_abbr():
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for i in range(8))


def is_valid_pmid(pmid):
    '''Check if a pmid is valid PMID

    Just a basic check
    '''
    # TODO implement this
    return True


def allowed_file_format(fn, exts=['csv', 'xls', 'xlsx', 'xml']):
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
    '''
    get JSONfied data
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
            'abstract': [],
            'raw_type': 'pubmed_xml',
            'xml': ET.tostring(item, encoding='utf8', method='xml')
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


def parse_ovid_exported_xml(full_fn):
    '''
    Parse the file from ovid export
    '''
    try:
        tree = ET.parse(full_fn)
        root = tree.getroot()
    except Exception as err:
        logger.error('ERROR when parsing %s, %s' % (full_fn, err))
        return None

    return _parse_ovid_exported_xml_root(root)


def parse_ovid_exported_xml_text(text):
    '''
    Parse the XML text from ovid export
    '''
    try:
        tree = ET.fromstring(text)
        try:
            root = tree.getroot()
        except:
            root = tree

    except Exception as err:
        logger.error('ERROR when parsing xml text, %s' % (err))
        return None

    return _parse_ovid_exported_xml_root(root)
    
    
def _parse_ovid_exported_xml_root(root):
    '''
    Parse a XML root which is an exported XML
    '''
    papers = []
    records = root.find('records').findall('record')
    # logger.info('found %s records in XML root' % (len(records)))
    for record in records:
        paper = {
            'pid': '',
            'pid_type': '',
            'title': '',
            'authors': '',
            'abstract': '',
            'pub_date': '',
            'pub_type': '',
            'journal': '',
            'rct_id': '',
            'raw_type': 'ovid_xml',
            'xml': ET.tostring(record, encoding='utf8', method='xml').decode('utf-8'),
            'other': {}
        }

        for node in record.iter():
            if node.tag == 'F':
                c = node.attrib['C']

                if c == 'UI':
                    # update the pid
                    paper['pid'] = __get_node_text(paper['pid'], node)
                elif c == 'ST':
                    # update the pid type by ST
                    paper['pid_type'] = __get_node_text(paper['pid_type'], node)
                elif c == 'DB':
                    # update the pid type by DB
                    paper['pid_type'] = __get_node_text(paper['pid_type'], node)
                elif c == 'TI':
                    # update the title
                    paper['title'] = __get_node_text(paper['title'], node)
                elif c == 'AU':
                    # update the authors
                    paper['authors'] = '; '.join([ _.text for _ in node.findall('D') ])
                elif c == 'AB':
                    # update the abstract
                    paper['abstract'] = __get_node_text(paper['abstract'], node)
                elif c == 'AS':
                    # update the journal by AS Abbreviated Source
                    paper['journal'] = __get_node_text(paper['journal'], node)
                elif c == 'SO':
                    # update the journal by SO
                    paper['journal'] = __get_node_text(paper['journal'], node)
                elif c == 'JA':
                    # update the journal by JA
                    paper['journal'] = __get_node_text(paper['journal'], node)
                elif c == 'YR':
                    # update the pub_date
                    paper['pub_date'] = __get_node_text(paper['pub_date'], node)
                elif c == 'DP':
                    # update the pub date by other info
                    paper['pub_date'] = __get_node_text(paper['pub_date'], node)
                elif c == 'PT':
                    # update the pub_type
                    paper['pub_type'] = __get_node_text(paper['pub_type'], node)
                elif c == 'CN':
                    # update the RCT id
                    paper['rct_id'] = __get_node_text(paper['rct_id'], node)
                else:
                    # unknow keywords
                    if c not in paper['other']:
                        paper['other'][c] = []
                    # extend this
                    paper['other'][c] += [ d.text for d in node.findall('D') ]
        
        papers.append(paper)

    return papers


def __get_node_text(old_text, node):
    '''
    Get the node text and return the option
    '''
    if node.find('D') is None:
        # if node is none, nothing to do
        return old_text

    # otherwise, get the text
    new_text = node.find('D').text.strip()

    if new_text == '':
        # if text is empty, just use the old text
        return old_text

    if old_text == '':
        # great! old text is empty, just use the new text
        return new_text

    # now is the hardest situation, both are not empty
    # TODO should decide the value by node type
    c = node.attrib['C']
    return new_text


def parse_endnote_exported_xml(full_fn):
    '''
    Parse the file from endnote export
    '''
    try:
        tree = ET.parse(full_fn)
        root = tree.getroot()
    except Exception as err:
        logger.error('ERROR when parsing %s, %s' % (full_fn, err))
        return None

    papers = []
    for record in tqdm(root.find('records').findall('record')):
        paper = {
            'pid': '',
            'pid_type': '',
            'title': '',
            'authors': [],
            'abstract': '',
            'pub_date': [],
            'pub_type': '',
            'journal': [],
            'raw_type': 'endnote_xml',
            # 'xml': ""
            'xml': ET.tostring(record, encoding='utf8', method='xml').decode('utf-8')
        }
        # print(paper)

        for node in record.iter():
            # print(node.tag)
            if node.tag == 'accession-num':
                paper['pid'] = ''.join(node.itertext())
            elif node.tag == 'remote-database-name':
                paper['pid_type'] = ''.join(node.itertext())
            elif node.tag == 'title':
                paper['title'] = ''.join(node.itertext())
            elif node.tag == 'author':
                paper['authors'].append(''.join(node.itertext()))

            # the journal information
            elif node.tag == 'full-title':
                paper['journal'].append(''.join(node.itertext()))
            elif node.tag == 'pages':
                paper['journal'].append('p. ' + ''.join(node.itertext()))
            elif node.tag == 'volume':
                paper['journal'].append('vol. ' + ''.join(node.itertext()))
            elif node.tag == 'number':
                paper['journal'].append('(%s)' % ''.join(node.itertext()))

            # the abstract
            elif node.tag == 'abstract':
                paper['abstract'] = ''.join(node.itertext())
                print('* found abstract: %s' % paper['abstract'])
                
            elif node.tag == 'pub-dates':
                paper['pub_date'].append( ' '.join(node.itertext()) )
            elif node.tag == 'dates':
                year = node.find('year')
                if year:
                    paper['pub_date'].append( ' '.join(node.find('year').itertext()) )
            elif node.tag == 'work-type':
                paper['pub_type'] = ''.join(node.itertext())

        # update the authors
        paper['authors'] = '; '.join(paper['authors'])
        paper['pub_date'] = check_paper_pub_date(' '.join(paper['pub_date']))
        paper['journal'] = check_paper_journal('; '.join(paper['journal']))
        paper['pid_type'] = check_paper_pid_type(paper['pid_type'])

        # if the pid is empty, just ignore this study
        paper['pid'] = check_paper_pid(paper['pid'])
        
        if paper['pid'] == '':
            pass
        else:
            papers.append(paper)

    return papers


def pred_rct(ti, ab):
    '''
    Predict if a study is RCT
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
    '''
    Get the today date string
    '''
    return datetime.datetime.today().strftime('%Y-%m-%d')


def get_nct_number(s):
    '''
    Get the NCT8 number from study
    '''
    return re.findall('NCT\d{8}', s, re.MULTILINE)


def get_year(s):
    '''
    Get the year number from a string
    '''
    rs = re.findall('\d{4}', s, re.MULTILINE)
    if len(rs) == 0:
        return ''
    else:
        return rs[0]


def save_pdf(file):
    '''
    Save the Upload file
    '''
    folder = datetime.datetime.now().strftime(settings.PATH_PDF_FOLDER_FORMAT)
    file_id = project_id = str(uuid.uuid1())
    file_name = file_id + '.pdf'

    # TODO make sure the display name is safe
    display_name = file.filename

    # save the file
    full_file_name = os.path.join(
        settings.PATH_PDF_FILES,
        folder,
        file_name
    )
    os.makedirs(os.path.dirname(full_file_name), exist_ok=True)
    file.save(full_file_name)

    # return the obj
    return {
        'folder': folder,
        'file_id': file_id,
        'display_name': display_name
    }


def delete_pdf(pdf_meta):
    '''
    Delete the PDF file
    '''
    full_fn = os.path.join(
        settings.PATH_PDF_FILES,
        pdf_meta['folder'],
        pdf_meta['file_id'] + '.pdf'
    )

    if os.path.exists(full_fn):
        os.remove(full_fn)

    return True


###############################################################################
# Check the input field to avoid invaild input values
###############################################################################

def check_paper_pid_type(pid_type):
    '''make a short pid type for input

    The PID type sometimes is too long for saving, make a shorter version
    from the original text
    '''
    if pid_type is None:
        return settings.PID_TYPE_NONE_TYPE

    # clean the leading and last blank space
    pid_type = pid_type.strip()
    if len(pid_type) == 0:
        return settings.PID_TYPE_NONE_TYPE
    else:
        return pid_type[0:settings.PID_TYPE_MAX_LENGTH]


def check_paper_pid(pid):
    '''check the paper pid for valid input
    '''
    if pid is None:
        return ''

    pid = pid.strip()
    if len(pid) == 0:
        return ''
    else:
        return pid[0:settings.PAPER_PID_MAX_LENGTH]


def check_paper_pub_date(pub_date):
    '''check the paper pub date for valid input
    '''
    if pub_date is None:
        return ''

    pub_date = pub_date.strip()
    if len(pub_date) == 0:
        return ''
    else:
        return pub_date[0:settings.PAPER_PUB_DATE_MAX_LENGTH]


def check_paper_journal(journal):
    '''check the paper journal for valid input
    '''
    if journal is None:
        return ''

    journal = journal.strip()
    if len(journal) == 0:
        return ''
    else:
        return journal[0:settings.PAPER_JOURNAL_MAX_LENGTH]


def escape_illegal_xml_characters(x):
    '''
    Make a safe XML content
    '''
    return re.sub(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]', '', x)


if __name__ == "__main__":
    fn = '/home/hehuan/Downloads/endnote_test.xml'
    fn = '/home/hehuan/Downloads/endnote_test_large.xml'
    fn = '/home/hehuan/Downloads/endnote_test_RCC.xml'
    papers = parse_endnote_exported_xml(fn)
    # pprint(papers)
    json.dump(papers, open('%s.json' % fn, 'w'), indent=2)
    print('* done!')