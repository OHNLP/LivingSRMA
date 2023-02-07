# Upgrader for LNMA system
#
# Please use this script very carefully!
# For most of time, just run once.
# Author: Huan He

from tqdm import tqdm 

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm.attributes import flag_modified

from lnma import settings, srv_project
from lnma import util
from lnma import dora
from lnma import ss_state
from lnma import models

from lnma import db
from lnma import create_app


def upgrade_pieces_from_extracts(keystr):
    '''
    Upgrade the pieces by getting data from extracts
    '''
    project = dora.get_project_by_keystr(keystr)
    if keystr == 'ALL_PRJS':
        extracts = dora.get_all_extracts()
    else:
        extracts = dora.get_extracts_by_keystr(keystr)
    print('* found %s extracts in the [%s]' % (len(extracts), keystr))

    for extract in tqdm(extracts):
        pieces = dora.create_or_update_pieces_by_extract_data(
            project.project_id,
            extract.extract_id,
            extract.data
        )

    print('* done upgrade the pieces for %s' % (keystr))


def upgrade_paper_meta_ds_id(keystr='TEST', force_update=False):
    '''
    Upgrade paper meta to include a ds_id information

    This is designed for de-duplication
    '''
    if keystr == 'ALL_PRJS':
        papers = dora.get_all_papers()
    else:
        papers = dora.get_papers_by_keystr(keystr)

    print('* found %s papers in the [%s]' % (len(papers), keystr))

    cnt_updated = 0
    cnt_not = 0
    for paper in tqdm(papers):
        has_updated = paper.update_meta_ds_id_by_self(force_update)

        if has_updated:
            # oh, this paper has been updated, need to save
            paper = dora._update_paper_meta(
                paper,
                auto_commit=False
            )
            cnt_updated += 1
        else:
            cnt_not += 1

        # batch commit
        if cnt_updated>0 and cnt_updated % 100 == 0:
            db.session.commit()

    # final commit
    db.session.commit()
    
    print('* done upgrading, %s have been updated, %s not or skipped.' % (
        cnt_updated, 
        cnt_not
    ))
    

def upgrade_project_settings(keystr):
    '''
    Upgrade project settings to support more features
    '''
    project = dora.get_project_by_keystr(keystr)

    if project is None:
        print('* ARE YOU KIDDING??? What is this [%s]?' % keystr)
        return

    # let's make a flag for showing whether this project is upgraded
    flag_upgraded = False

    # the auto_fill is for data extraction
    if 'auto_fill' in project.settings:
        print('* found auto_fill in [%s]' % keystr)

    else:
        # ok, let's give a default sample for this project
        project.settings['auto_fill'] = [
        {
            "from": "TRIAL CHARACTERISTICS|Treatment regimen",
            "to": "Treatment Arm|Treatment"
        },
        {
            "from": "TRIAL CHARACTERISTICS|Control regimen",
            "to": "Control Arm|Control"
        }]
        print('* added default auto_fill to [%s]' % (keystr))
        flag_upgraded = True

    # the clinical_questions is for screening and extraction
    if 'clinical_questions' in project.settings:
        print('* found clinical_questions in [%s]' % keystr)
        for cq in project.settings['clinical_questions']:
            print('*   cq %s: %s' % (cq['abbr'], cq['name']))

    else:
        # Ok, let's just put a default cq
        project.settings['clinical_questions'] = [{
            "abbr": "default",
            "name": project.title
        }]
        print('* added default clinical question to [%s]' % (keystr))
        flag_upgraded = True

    # the `outcome` attr is for data extraction
    if 'outcome' in project.settings:
        print('* found outcome in [%s]' % keystr)
    
    else:
        project.settings['outcome'] = {
            "nma": {
                "analysis_groups": [
                    {
                        "abbr": "primary",
                        "name": "Primary Analysis"
                    },
                    {
                        "abbr": "sensitivity",
                        "name": "Sensitivity Analysis"
                    }
                ],
                "default_setting": {
                    "input_format": "NMA_PRE_SMLU"
                }
            },
            "pwma": {
                "analysis_groups": [
                    {
                        "abbr": "primary",
                        "name": "Primary Analysis"
                    },
                    {
                        "abbr": "sensitivity",
                        "name": "Sensitivity Analysis"
                    },
                    {
                        "abbr": "subgroup",
                        "name": "Subgroup Analysis"
                    }
                ],
                "default_setting": {
                    "input_format": "PRIM_CAT_RAW"
                }
            }
        }
        print('* added default outcome to [%s]' % (keystr))
        flag_upgraded = True

    # the outcomes_enabled is for screening and extraction
    if 'outcomes_enabled' in project.settings:
        print("* found outcomes_enabled in [%s]" % keystr)

    else:
        # Ok, let's just put a default enabled outcomes
        project.settings['outcomes_enabled'] = [
            'pwma', 
            'nma'
        ]
        print("* found outcomes_enabled in [%s]" % keystr)
        flag_upgraded = True

    if flag_upgraded:
        # let's upgrade the project 
        flag_modified(project, 'settings')
        db.session.add(project)
        db.session.commit()
        print('* commited changes to database to [%s]' % (keystr))

    else:
        print('* skipped commit due to no changes to [%s]' % (keystr))
    
    print('* done upgrading with [%s]' % keystr)



def upgrade_paper_ss_ex_label_for_user(keystr):
    '''
    Upgrade the paper's label
    '''
    project = dora.get_project_by_keystr(keystr)
    papers = dora.get_papers_by_keystr(keystr)

    print('* found %d papers for [%s] in current database' % (
        len(papers), keystr
    ))

    cnt = {
        'total': 0
    }

    for paper in tqdm(papers):
        if 'label' in paper.ss_ex:
            has_update = False
            for label in paper.ss_ex['label']:
                if 'user' in paper.ss_ex['label'][label]:
                    continue
                else:
                    paper.ss_ex['label'][label]['user'] = {
                        'uid': settings.SYSTEM_ADMIN_UID,
                        'abbr': settings.SYSTEM_ADMIN_NAME
                    }
                    has_update = True

            if has_update:
                flag_modified(paper, "ss_ex")
                cnt['total'] += 1

                db.session.add(paper)
                db.session.commit()

    print('* found and upgraded %s studies for the ss_cq' % (
        cnt['total']
    ))

    print('* done upgrading papers')
    


def upgrade_paper_ss_ex_for_cq(keystr):
    '''
    Upgrade the paper data model `ss_ex` to support cq-based data.

    ALL ss_rs==f1,f2,f3 papers are affected.
    '''
    srv_project.update_project_papers_ss_cq_by_keystr(
        keystr,
        settings.PAPER_SS_EX_SS_CQ_DECISION_YES
    )

    print('* done upgrading papers')



def upgrade_extract_coe_ds(keystr):
    '''
    Upgrade the data structure of the CoE for all extracts in a project

    It will add one 'main' layer to the CoE to support multi-ma in single outcome,
    which means that under a single outcome, there can be multiple CoE for multiple MAs.
    This is designed for IO project and other similar needs.
    '''
    import copy

    # get all extracts of this project
    extracts = dora.get_extracts_by_keystr(keystr)
    print('* found %s extracts in [%s]' % (
        len(extracts), keystr
    ))

    # now, check each extract
    updated_exts = []
    
    for extract in tqdm(extracts):
        # first, check the coe
        if 'coe' not in extract.meta:
            # it's ok, dont modify as this outcome is not affected.
            print('* skip non-coe extract', extract.get_repr_str())
            continue

        # second, check if it's the new data structure
        if 'main' in extract.meta['coe']:
            print('* skip new-ds extract', extract.get_repr_str())

        # OK, need to update
        main_coe = copy.deepcopy(extract.meta['coe'])

        # update the structure
        extract.meta['coe'] = {
            'main': main_coe
        }

        # no matter what we do, update this extract here
        updated_ext = dora.update_extract(extract)
        updated_exts.append(updated_ext)
        print('* updated extract', extract.get_repr_str())

    print('*' * 80)
    print('* updated %s extracts' % (
        len(updated_exts)
    ))
    print('* done upgrading extracts')


def upgrade_extract_data_model_for_subg_and_cq(keystr):
    '''
    Upgrade the data model for all extracts in a project
    to support the subg analysis and cq-based data.
    '''
    import copy

    extracts = dora.get_extracts_by_keystr(keystr)
    print('* found %s extracts in [%s]' % (
        len(extracts), keystr
    ))

    # now, check each extract
    updated_exts = []
    
    for extract in tqdm(extracts):
        # first, check the new attr `cq_abbr`
        if 'cq_abbr' not in extract.meta:
            # now, let's add something
            extract.meta['cq_abbr'] = 'default'
        
        # for the subg
        if 'is_subg_analysis' not in extract.meta:
            extract.meta['is_subg_analysis'] = 'no'

        if extract.meta['is_subg_analysis'] == 'no':
            extract.meta['sub_groups'] = ['A']

        if 'treatments' not in extract.meta:
            extract.meta['treatments'] = ['A', 'B']

        # now, let's check the data
        for pid in extract.data:
            # check the main arm
            if 'g0' in extract.data[pid]['attrs']['main']:
                # this pid is updated
                continue

            # copy the main
            m = copy.deepcopy(extract.data[pid]['attrs']['main'])

            # update the content
            extract.data[pid]['attrs']['main'] = {
                'g0': m
            }

            # check other arms
            if len(extract.data[pid]['attrs']['other']) == 0:
                # no need to convert empty other arms
                continue

            new_other = []
            for other_idx in range(len(extract.data[pid]['attrs']['other'])):
                # copy the data in this arm
                d = copy.deepcopy(extract.data[pid]['attrs']['other'][other_idx])

                # put the other arm into new_other
                new_other.append({
                    'g0': d
                })
            # update the other arm
            extract.data[pid]['attrs']['other'] = new_other

        # no matter what we do, update this extract here
        updated_ext = dora.update_extract(extract)
        updated_exts.append(updated_ext)

    print('* updated %s extracts' % (
        len(updated_exts)
    ))
    print('* done upgrading extracts')


if __name__ == '__main__':
    app = create_app()
    db.init_app(app)
    app.app_context().push()

    # upgrade something?
    keystr = 'LUNGCA'
    upgrade_paper_meta_ds_id(keystr, False)
    print("*" * 60)
    print('\n\n')
    upgrade_pieces_from_extracts(keystr)

    print('* done upgrader')
