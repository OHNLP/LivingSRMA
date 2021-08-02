from tqdm import tqdm 

from lnma import settings
from lnma import util
from lnma import dora
from lnma import ss_state
from lnma import models


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
        flag_upgraded = True

    # the clinical_questions is for screening and extraction
    if 'clinical_questions' in project.settings:
        print("* found clinical_questions in [%s]" % keystr)

    else:
        # Ok, let's just put a default cq
        project.settings['clinical_questions'] = [{
            "abbr": "default",
            "name": project.title
        }]
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
        flag_upgraded = True
    
    print('* done upgrading with [%s]' % keystr)


def upgrade_paper_ss_ex_for_cq(keystr):
    '''
    Upgrade the paper data model `ss_ex` to support cq-based data.

    ALL ss_rs==f1,f2,f3 papers are affected.
    '''
    project = dora.get_project_by_keystr(keystr)
    papers = dora.get_papers_by_keystr(keystr)

    print('* found %d papers in current database' % len(papers))

    cnt = {

    }

    for paper in tqdm(papers):
        if paper.is_ss_included_in_project():
            pass


def upgrade_extract_data_model_for_subg_and_cq(keystr):
    '''
    Upgrade the data model for all extracts in a project
    to support the subg analysis and cq-based data.
    '''
    import copy

    extracts = dora.get_extracts_by_keystr(keystr)

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

    return updated_exts