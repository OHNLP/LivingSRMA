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
        settings.PAPER_SS_EX_SS_CQ_YES
    )

    print('* done upgrading papers')


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

    # 
    print('* done upgrader')
