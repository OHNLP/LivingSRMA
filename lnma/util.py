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


def mk_number_str(length=6):
    '''
    Make a random str of numbers
    '''
    return ''.join(random.choice('0123456789') for i in range(length))


def mk_empty_extract_paper_data(is_selected=False):
    '''
    Make an empty extract paper data
    '''
    return {
        'is_selected': is_selected,
        'is_checked': False,
        'n_arms': 2,
        'attrs': {
            'main': {},
            'other': []
        }
    }


def fill_extract_data_arm(arm, cate_attrs):
    '''
    Fill the extract data arm with empty values
    The arm could be main (arm 1) or other arm
    '''
    for cate in cate_attrs:
        for attr in cate['attrs']:
            attr_abbr = attr['abbr']
            if attr['subs'] is None:
                if attr_abbr not in arm:
                    arm[attr_abbr] = ''
                else:
                    # which means this attr exsits
                    pass
            else:
                # have multiple subs
                for sub in attr['subs']:
                    sub_abbr = sub['abbr']
                    if sub_abbr not in arm:
                        arm[sub_abbr] = ''

    return arm


def is_same_extraction(ea, eb):
    '''
    Compare two extractions attr by attr
    '''
    if ea['is_selected'] != eb['is_selected']:
        return False
    
    if ea['is_checked'] != eb['is_checked']:
        return False
    
    if ea['n_arms'] != eb['n_arms']:
        return False

    # check the main arm from ea side
    for attr in ea['attrs']['main']:
        if attr not in eb['attrs']['main']:
            # which means eb use different meta???
            return False
        
        if ea['attrs']['main'][attr] != eb['attrs']['main'][attr]:
            return False

    # 2021-06-04: two side check update
    # we found that when updating the itable design
    # one side check couldn't figure out the changes
    # check the main arm from eb side
    for attr in eb['attrs']['main']:
        if attr not in ea['attrs']['main']:
            # which means ea use different meta???
            return False
        
        if eb['attrs']['main'][attr] != ea['attrs']['main'][attr]:
            return False

    # check other arms
    if len(ea['attrs']['other']) != len(eb['attrs']['other']):
        return False

    # check each arm in other
    for arm_idx, _ in enumerate(ea['attrs']['other']):
        ea_arm = ea['attrs']['other'][arm_idx]
        eb_arm = eb['attrs']['other'][arm_idx]

        # check from ea side
        for attr in ea_arm:
            if attr not in eb_arm:
                # which means eb use different meta???
                return False
            
            if ea_arm[attr] != eb_arm[attr]:
                return False

        # 2021-06-04: two side check
        for attr in eb_arm:
            if attr not in ea_arm:
                # which means eb use different meta???
                return False
            
            if eb_arm[attr] != ea_arm[attr]:
                return False
            
    # wow, they are the same
    return True
    

def is_valid_rct_id(rct_id):
    '''
    Check if a RCT ID is valid

    currently, there is not a good way to know
    '''
    if len(rct_id)>5:
        return True

    return False


def is_valid_pmid(pmid):
    '''
    Check if a pmid is valid PMID

    Just a basic check
    '''
    valid_pmids = re.findall('\d{8}', pmid, re.MULTILINE)

    if valid_pmids == []:
        return False
    else:
        return True


def get_valid_pmid(pmid):
    '''
    Get the valid PMID from a pmid string (candidate)
    '''
    valid_pmids = re.findall('\d{8}', pmid, re.MULTILINE)

    if valid_pmids == []:
        return None
    else:
        return valid_pmids[0]


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
    '''
    Search for term in pubmed
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
    '''
    Get summary of pmid list
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
    '''
    Get the raw xml data from pubmed
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
            'date_pub': [],
            'date_epub': [],
            'date_revised': [],
            'date_completed': [],
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

            # 2021-03-24: there are four types of date
            # take this for example: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=27717298&retmode=xml
            # I guess
            # - ArticleDate is the ePub date
            # - PubDate is the journal physical publication date
            # - DateCompleted is ... I don't know
            # - DateRevised is the online revision date
            # in the last, if ArticleDate is available, just use ArticleDate
            # if not, follow the order above

            elif node.tag == 'ArticleDate':
                for c in node:
                    paper['date_epub'].append(c.text)

            elif node.tag == 'PubDate':
                for c in node:
                    paper['date_pub'].append(c.text)

            elif node.tag == 'DateCompleted':
                for c in node:
                    paper['date_completed'].append(c.text)

            elif node.tag == 'DateRevised':
                for c in node:
                    paper['date_revised'].append(c.text)
                
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

        # try to find the good date
        paper['date_epub'] = '-'.join(paper['date_epub'])
        paper['date_pub'] = '-'.join(paper['date_pub'])
        paper['date_completed'] = '-'.join(paper['date_completed'])
        paper['date_revised'] = '-'.join(paper['date_revised'])

        if paper['date_epub'] != '':
            paper['sortpubdate'] = paper['date_epub']
        elif paper['date_pub'] != '':
            paper['sortpubdate'] = paper['date_pub']
        elif paper['date_pub'] != '':
            paper['sortpubdate'] = paper['date_completed']
        elif paper['date_pub'] != '':
            paper['sortpubdate'] = paper['date_revised']
        else:
            paper['sortpubdate'] = ''

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
            'xml': ET.tostring(record, encoding='utf8', method='xml').decode('utf-8'),
            'other': {}
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
            else:
                if node.tag not in paper['other']:
                    paper['other'][node.tag] = []
                paper['other'][node.tag] += list(node.itertext())

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


def parse_ovid_exported_text_content(txt):
    '''
    Parse the email content from OVID 

    This is for the text format
    '''
    # open('tmp.txt', 'w').write(txt)

    lines = txt.split('\n')
    ptn_attr = r'^\s*([A-Z]{2})\s+-\s(.*)'
    ptn_attr_ext = r'^\s+(.*)'
    ptn_new_art = r'^\s*\<(\d+)\>'

    arts = []

    # temporal variable
    art = {}
    attr = ''
    buff = []

    for line in lines:
        buff.append(line)
        # try articl pattern
        m = re.findall(ptn_new_art, line)
        if len(m) > 0:
            # this means this line starts a new article
            # for example
            # re.findall(ptn_new_art, '<13>')
            # the 13rd article is found
            if art == {}:
                # it means this is the first article
                pass
            else:
                # not the first, save previous first, then reset
                art['text'] = '\n'.join(buff)
                arts.append(art)
                art = {}
                buff = []
            
            # once match a pattern, no need to check other patterns
            continue

        # try attr pattern first, it's the most common pattern
        m = re.findall(ptn_attr, line)
        if len(m) > 0:
            # which means it's a new attribute
            # for example
            # > re.findall(ptn_attr, 'DB  - Ovid MEDLINE(R) Revisions')
            # > [('DB', 'Ovid MEDLINE(R) Revisions')]
            attr = m[0][0]
            val = m[0][1].strip()

            # auto seg by UI
            if attr == 'UI' and 'UI' in art:
                art['text'] = '\n'.join(buff)
                arts.append(art)
                art = {}
                buff = []

            # append this attr
            if attr not in art: art[attr] = []

            # put this value into art object
            art[attr].append(val)

            # once match a pattern, no need to check other patterns
            continue

        # try next pattern
        m = re.findall(ptn_attr_ext, line)
        if len(m) > 0:
            # this means this line is an extension of previous attr
            val = m[0]
            # use previous attr, the attr should exist
            if attr == '':
                pass
            else:
                if attr not in art: art[attr] = []
                art[attr].append(val)

                # once match a pattern, no need to check other patterns
                continue

    
    # usually, the last art need to be appended manually
    if art != {}:
        art['text'] = '\n'.join(buff)
        arts.append(art)
        buff = []

    # now need to merge the attributes 
    for art in arts:
        for k in art:
            if len(art[k]) == 1:
                art[k] = art[k][0]
            else:
                if k in ('AU', 'FA', 'ID'): continue
                elif k == 'AB': art[k] = '\n'.join(art[k])
                else: art[k] = ' '.join(art[k])

    # convert the articles to paper format
    papers = []

    for art in arts:
        if 'UI' not in art:
            continue

        pid = art['UI']
        title = art['TI'] if 'TI' in art else ''
        abstract = art['AB'] if 'AB' in art else ''
        authors = ', '.join(art['AU']) if 'AU' in art else ''
        pid_type = art['DB'].upper() if 'DB' in art else 'OVID'
        pub_type = art['PT'] if 'PT' in art else ''
        rct_id = art['CN'] if 'CN' in art else ''

        if pid_type.startswith('EMBASE'):
            pub_date = art['DP'] if 'DP' in art else ''
            journal = art['JA'] if 'JA' in art else ''
        elif pid_type.startswith('OVID MEDLINE'):
            pub_date = art['EP'] if 'EP' in art else ''
            journal = art['AS'] if 'AS' in art else ''
        else:
            pub_date = art['EP'] if 'EP' in art else ''
            journal = art['AS'] if 'AS' in art else ''

        paper = {
            'pid': pid,
            'pid_type': pid_type,
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'pub_date': pub_date,
            'pub_type': pub_type,
            'journal': journal,
            'rct_id': rct_id,
            'raw_type': 'text',
            'xml': '',
            'other': art
        }

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


def get_decision_detail_dict(reason, decision):
    '''
    Get a decision detail dictionary
    '''
    # create a dict for the details
    detail_dict = {
        'date_decided': get_today_date_str(),
        'reason': reason,
        'decision': decision
    }

    return detail_dict


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


def get_author_etal_from_authors(authors):
    '''
    Get the "First author name et al" format
    '''
    aus = authors.split(';')
    if len(aus) == 1:
        aus = authors.split(',')

    if len(aus[0]) > 20:
        aus = aus[0].split(',')
    
    fau_etal = aus[0] + ' et al'

    return fau_etal


def get_author_etal_from_paper(paper):
    '''
    Get the "First author name et al" format
    '''
    return get_author_etal_from_authors(paper.authors)


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


def save_pdfs_from_request_files(files):
    '''
    Save the uploaded files in the request
    and return the pdf_metas for paper.meta['pdfs']

    The `files` is a request form object which contains every file
    '''
    # save the files first
    pdf_metas = []
    for file in files:
        if file and allowed_file(file.filename):
            pdf_meta = save_pdf(file)
            pdf_metas.append(pdf_meta)

    return pdf_metas


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


def make_temp_pid():
    pid_type = 'TEMP_PID'
    pid = 'TMP' + mk_number_str()

    return pid, pid_type


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_PDF_UPLOAD_EXTENSIONS


###########################################################
# Shared data functions
###########################################################
def notna(v):
    '''
    Check whether a value `v` is NA or not
    '''
    return not (v is None or v == '' or v== 'null')


def notzero(v):
    '''
    Check whether a value `v` is 0
    '''
    return v!=0


def is_pwmable(Et, Nt, Ec, Nc):
    '''
    Check whether a study is able to do PWMA
    '''
    # the first condition is all numbers are not null
    f1 = notna(Et) and notna(Nt) and \
         notna(Ec) and notna(Nc)
        
    # the second condition is not both zero
    f2 = (notna(Et) and notzero(Et)) or \
         (notna(Ec) and notzero(Ec))

    # final combine two
    return f1 and f2


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


def json_encoder(o):
    '''
    Encode the object `o` in for JSON
    '''
    if isinstance(o, datetime.datetime):
        return o.__str__()

    return str(o)
    

if __name__ == "__main__":
    fn = '/home/hehuan/Downloads/endnote_test.xml'
    fn = '/home/hehuan/Downloads/endnote_test_large.xml'
    fn = '/home/hehuan/Downloads/endnote_test_RCC.xml'
    papers = parse_endnote_exported_xml(fn)
    # pprint(papers)
    json.dump(papers, open('%s.json' % fn, 'w'), indent=2)
    print('* done!')