import pandas as pd

from lnma import dora
from lnma import srv_extract
from lnma import util


def get_itable_attr_rs_cfg_from_db(keystr, cq_abbr="default"):
    '''
    Get everything related to itable from db
    '''
    # get the paper data as well
    # the itable is a special extract for this project

    project = dora.get_project_by_keystr(keystr)
    if project is None:
        return None

    project_id = project.project_id

    # get the extract
    extract = srv_extract.get_itable_by_project_id_and_cq_abbr(
        project_id, cq_abbr
    )
    if extract is None:
        return None

    # get the papers for this project
    papers = dora.get_papers_of_included_sr(project_id)
    paper_dict = {}
    for p in papers:
        paper_dict[p.pid] = p

    # this is for output as some papers are not selected for output
    selected_paper_dict = {}

    # get the stat selected for itable
    # stat = {
    #     'f3': {
    #         'pids': [],
    #         'rcts': [],
    #         'n': 0
    #     }
    # }
    stat_f3 = srv_extract.get_studies_included_in_ma(
        keystr, 
        cq_abbr,
        paper_dict
    )
    if stat_f3 is None:
        stat_f3 = []
    else:
        stat_f3 = stat_f3['f3']['pids']

    # get the extract meta and data
    meta = extract.meta
    data = extract.data

    # the data needed for the itable frontend
    rs = []
    cfg = {}
    attrs = []

    abbr2attr_name = {}
    # convert the format for attrs
    for cate in meta['cate_attrs']:
        for attr in cate['attrs']:
            if attr['subs'] is None or attr['subs'] == []:
                attr_name = "%s" % attr['name']
                attr_id = ("_%s|%s" % (attr['name'], attr['name'])).upper()
                abbr2attr_name[attr['abbr']] = attr_name

                attrs.append({
                    "attr_id": attr_id, 
                    "branch": "%s" % attr['name'], 
                    "cate": "%s" % cate['name'], 
                    "name": attr_name, 
                    "trunk": "_%s" % attr['name'], 
                    "vtype": "text"
                })

            else:
                for sub in attr['subs']:
                    attr_name = "%s | %s" % (attr['name'], sub['name'])
                    attr_id = ("%s|%s" % (attr['name'], sub['name'])).upper()
                    abbr2attr_name[sub['abbr']] = attr_name

                    attrs.append({
                        "attr_id": attr_id, 
                        "branch": "%s" % sub['name'], 
                        "cate": "%s" % cate['name'], 
                        "name": attr_name, 
                        "trunk": "%s" % attr['name'], 
                        "vtype": "text"
                    })

    # after the attributes in the `extract.meta`, which are customized for itable,
    # need to add those "basic" attributes, which just some information for paper.
    basic_attrs = [
        { 'abbr': 'ba_included_in_ma', 'name': 'Included in MA', },
        { 'abbr': 'ba_ofu', 'name': 'Original/Follow Up',        },
        { 'abbr': 'ba_year', 'name': 'Year',                     },
        { 'abbr': 'ba_authors', 'name': 'Authors',               },
        { 'abbr': 'ba_pmid', 'name': 'PMID',                     },
        { 'abbr': 'ba_nct', 'name': 'NCT',                       },
    ]
    first_cate = attrs[0]['cate']
    for attr in basic_attrs:
        attr_name = "%s" % attr['name']
        attr_id = ("_%s|%s" % (attr['name'], attr['name'])).upper()
        abbr2attr_name[attr['abbr']] = attr_name
        attrs.insert(0, {
            "attr_id": attr_id, 
            "branch": "%s" % attr['name'], 
            "cate": first_cate, 
            "name": attr_name, 
            "trunk": "_%s" % attr['name'], 
            "vtype": "text"
        })
    
    # 2021-08-08: to insert the data from other arms
    # we abstract the function for getting `r`
    def _make_r(paper_data, abbr_dict, other_arm=False):
        # `r` use name as key to retrive data, 
        # which is used in the itable.html.
        # but the case here is quite complex, the multi-arm issue
        # let's append the main track
        # the paper_ext is a dictionary:
        # 2021-08-08: the data structure in extracted data have been updated
        # for itable, there is only one group `g0` in all arms
        #
        # {
        #    'attrs': {
        #         'main': {
        #              g0: {
        #                   abbr: value
        #              }
        #         },
        #         'other': [{
        #              g0: {
        #                   abbr: value
        #              }
        #         }]
        #    }
        #    'n_arms':
        #    'is_checked':
        #    'is_selected':
        # }
        #
        # So, please check the data carefully.
        r = {}

        for abbr in abbr_dict:
            attr_name = abbr_dict[abbr]
            if abbr in paper_data:
                r[attr_name] = paper_data[abbr]
            else:
                # in most case, the value should be there
                # but ... you know ... I don't know what happens
                # just give an empty value to avoid any issue in rendering
                r[attr_name] = ''

        # add the basic features
        for attr in basic_attrs:
            attr_name = "%s" % attr['name']
            if attr['abbr'] == 'ba_year':
                val = paper.get_year()
            elif attr['abbr'] == 'ba_authors':
                # the author name maybe different format, use paper instead of `r`
                auetal = util.get_author_etal_from_paper(paper)

                # add some information of other arms
                if other_arm:
                    val = auetal + '*'
                else:
                    val = auetal

            elif attr['abbr'] == 'ba_ofu':
                val = paper.get_study_type()

            elif attr['abbr'] == 'ba_pmid':
                val = paper.pid

            elif attr['abbr'] == 'ba_nct':
                val = paper.meta['rct_id']

            elif attr['abbr'] == 'ba_included_in_ma':
                val = 'yes' if paper.pid in stat_f3 else 'no'

            else:
                val = 'NA'

            r[attr_name] = val

        return r

    # now convert the records
    # first, we need to understand that, maybe not all of the f1, f2, and f3
    # are used in the itable, the only way to decide that is the `is_selected`
    # flag in the `extract.data`.
    # so, when getting the `rs`, the main loop is to get the studies

    for pid in data:
        paper_ext = data[pid]

        if paper_ext['is_selected'] == False: continue

        # now, let's parse this paper
        # paper = dora.get_paper_by_project_id_and_pid(project_id, pid)
        if pid not in paper_dict:
            # what???
            print('* MISSING %s when building ITABLE.json' % pid)
            continue

        # get this paper from dict instead of SQL
        paper = paper_dict[pid]

        # add this paper to dict for output
        selected_paper_dict[pid] = paper.as_extreme_simple_dict()
        
        # the `r` is for the output
        # first, let's get the main arm
        r = _make_r(paper_ext['attrs']['main']['g0'], abbr2attr_name, False)
        rs.append(r)

        # check other arms
        if paper_ext['n_arms'] > 2:
            # ok, multi-arms!
            for arm_idx in range(paper_ext['n_arms'] - 2):
                r = _make_r(
                    paper_ext['attrs']['other'][arm_idx]['g0'], 
                    abbr2attr_name,
                    True
                )
                rs.append(r)
        
    # cols for display
    cfg['cols'] = {
        'default': ['Authors'],
        'fixed': ['Authors']
    }
    # add the default attrs
    if 'default_attrs' in meta:
        cfg['cols']['default'] += meta['default_attrs']
    
    # last thing is the filter
    # filter is in the meta
    # add the filters
    if 'filters' in meta:
        cfg['filters'] = meta['filters']
    else:
        cfg['filters'] = []

    # add the default filter All 
    for filter in cfg['filters']:
        if 'ALL' not in filter['values'][0]['display_name'].upper():
            filter['values'].insert(0, {
                'default': True,
                'display_name': 'All',
                'sql_cond': '1=1',
                'value': 0
            })

    # finally, finished!
    ret = {
        'rs': rs,
        'cfg': cfg,
        'attrs': attrs,
        'paper_dict': selected_paper_dict
    }

    return ret


def get_attr_pack_from_itable(full_fn):
    # read data, hope it is xlsx format ...
    if full_fn.endswith('csv'):
        df = pd.read_csv(full_fn, header=None, nrows=2)
    else:
        df = pd.read_excel(full_fn, header=None, nrows=2)

    # convert to other shape
    dft = df.T
    df_attrs = dft.rename(columns={0: 'cate', 1: 'name'})

    # not conver to tree format
    attr_dict = {}
    attr_tree = {}

    for idx, row in df_attrs.iterrows():
        vtype = 'text'
        name = row['name'].strip()
        cate = row['cate'].strip()

        # split the name into different parts
        name_parts = name.split('|')
        if len(name_parts) > 1:
            trunk = name_parts[0].strip()
            branch = name_parts[1].strip()
        else:
            trunk = '_' + name
            branch = name
        attr_id = trunk.upper() + '|' + branch.upper()

        if cate not in attr_tree: attr_tree[cate] = {}
        if trunk not in attr_tree[cate]: attr_tree[cate][trunk] = []

        attr = {
            'name': name,
            'cate': cate,
            'vtype': vtype,
            'trunk': trunk,
            'branch': branch,
            'attr_id': attr_id,
        }
        # pprint(attr)

        # put this item into dict
        attr_tree[cate][trunk].append(attr)
        attr_dict[attr_id] = attr

    return { 'attr_dict': attr_dict, 'attr_tree': attr_tree }