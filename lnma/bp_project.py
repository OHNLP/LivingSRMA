from flask import json, request
from flask import flash
from flask import render_template
from flask import Blueprint
from flask import jsonify
from flask import current_app
from flask import redirect
from flask import url_for

from flask_login import login_required
from flask_login import current_user

from lnma import dora, settings, srv_project

bp = Blueprint("project", __name__, url_prefix="/project")

@bp.route('/')
@login_required
def index():
    return render_template('project/index.html')


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('project/create.html')

    query = request.form.get('query')

    project, msg = dora.create_project(
        owner_uid = current_user.uid,
        title = request.form.get('title'),
        keystr = request.form.get('keystr'),
        abstract = request.form.get('abstract'),
        p_settings=None
    )
    if project is None:
        flash('Failed. This project Identifier already exists, please use other Identifier and try again', 'error')
        return redirect(url_for('project.create'))
    else:
        flash('Project is created!')
        return redirect(url_for('project.mylist'))



@bp.route('/mylist', methods=['GET', 'POST'])
@login_required
def mylist():
    if request.method == 'GET':
        return render_template('project/list.html')
    projects = dora.list_projects_by_uid(current_user.uid)


@bp.route('/editor')
@login_required
def editor():
    project_id = request.cookies.get('project_id')
    if project_id is None or project_id == '':
        flash('Set working project first')
        return redirect(url_for('project.mylist'))

    project = dora.get_project(project_id)

    # preprocessing the tags
    form_textarea_tags = project.get_tags_text()

    # preprocessing the ie criterias
    form_textarea_inclusion_criterias = project.get_inclusion_criterias_text()

    # preprocessing the ie criterias
    form_textarea_exclusion_criterias = project.get_exclusion_criterias_text()

    # preprocessing the exclusion reasons
    form_textarea_exclusion_reasons = project.get_exclusion_reasons_text()

    # preprocessing the ie keywords
    form_textarea_inclusion_keywords = project.get_inclusion_keywords_text()

    # preprocessing the exclusion keywords
    form_textarea_exclusion_keywords = project.get_exclusion_keywords_text()

    # the pdf keywords
    form_textarea_pdf_keywords = project.get_pdf_keywords_text()

    # the all settings JSON string
    form_textarea_settings = project.get_settings_text()

    return render_template('project/editor.html', 
        project=project,
        form_textarea_tags=form_textarea_tags,
        form_textarea_inclusion_criterias=form_textarea_inclusion_criterias,
        form_textarea_exclusion_criterias=form_textarea_exclusion_criterias,
        form_textarea_exclusion_reasons=form_textarea_exclusion_reasons,
        form_textarea_inclusion_keywords=form_textarea_inclusion_keywords,
        form_textarea_exclusion_keywords=form_textarea_exclusion_keywords,
        form_textarea_pdf_keywords=form_textarea_pdf_keywords,
        form_textarea_settings=form_textarea_settings
    )


@bp.route('/public_website', methods=['GET'])
@login_required
def public_website():
    project_id = request.cookies.get('project_id')
    cq_abbr = request.cookies.get('cq_abbr')

    if project_id is None:
        return redirect(url_for('project.mylist'))

    if cq_abbr is None:
        cq_abbr = 'default'

    project = dora.get_project(project_id)

    return render_template(
        'project/public_website.html',
        cq_abbr=cq_abbr,
        project=project,
        project_json_str=json.dumps(project.as_dict())
    )


###############################################################
# APIs for project
###############################################################

@bp.route('/api/list')
@login_required
def api_list():
    projects = dora.list_projects_by_uid(current_user.uid)

    ret = {
        'success': True,
        'projects': [ project.as_dict() for project in projects ]
    }

    return jsonify(ret)


@bp.route('/api/get_project')
@login_required
def api_get_project():
    projects = dora.list_projects_by_uid(current_user.uid)

    ret = {
        'success': True,
        'projects': [ project.as_dict() for project in projects ]
    }

    return jsonify(ret)


@bp.route('/api/add_user_to_project', methods=['GET', 'POST'])
@login_required
def api_add_user_to_project():
    if request.method == 'GET':
        return redirect(url_for('project.mylist'))

    to_add_uid = request.form.get('uid', None)
    project_id = request.form.get('project_id', None)
    current_user_uid = current_user.uid

    # TODO validate the project is belong to current user

    # add the to_add_uid
    to_add_user, project = dora.add_user_to_project(to_add_uid, project_id)

    # TODO check the result
    
    flash("Added %s to Project [%s]" % (to_add_user.uid, project.title))

    return redirect(url_for('project.mylist'))


@bp.route('/api/api_set_criterias', methods=['GET', 'POST'])
@login_required
def api_set_criterias():
    if request.method == 'GET':
        return redirect(url_for('project_editor'))
        
    project_id = request.cookies.get('project_id')
    if project_id is None or project_id == '':
        flash('Set working project first')
        return redirect(url_for('project.mylist'))

    raw_inclusion_criterias = request.form.get('form_textarea_inclusion_criterias')
    raw_exclusion_criterias = request.form.get('form_textarea_exclusion_criterias')

    # remove blank
    raw_inclusion_criterias = raw_inclusion_criterias.strip()
    raw_exclusion_criterias = raw_exclusion_criterias.strip()

    # update
    is_success, project = dora.set_project_criterias(
        project_id, raw_inclusion_criterias, raw_exclusion_criterias
    )

    flash('Saved inclusion/exclusion criterias!')
    return redirect(url_for('project.editor', _anchor="ie_criteria_info"))


@bp.route('/api/set_exclusion_reasons', methods=['GET', 'POST'])
@login_required
def api_set_exclusion_reasons():
    if request.method == 'GET':
        return redirect(url_for('project_editor'))
        
    project_id = request.cookies.get('project_id')
    if project_id is None or project_id == '':
        flash('Set working project first')
        return redirect(url_for('project.mylist'))

    raw_exclusion_reasons = request.form.get('form_textarea_exclusion_reasons')

    # remove blank
    raw_exclusion_reasons = raw_exclusion_reasons.strip()

    # split
    exclusion_reasons = raw_exclusion_reasons.split('\n')
    
    # remove empty
    exclusion_reasons_cleaned = []
    for t in exclusion_reasons:
        t = t.strip()
        if t == '':
            pass
        else:
            exclusion_reasons_cleaned.append(t)

    # update
    is_success, project = dora.set_project_exclusion_reasons(
        project_id, exclusion_reasons_cleaned
    )

    flash('Saved %s exclusion_reasons!' % (
        len(exclusion_reasons_cleaned),
    ))
    return redirect(url_for('project.editor', _anchor="ex_reason_info"))


@bp.route('/api/set_highlight_keywords', methods=['GET', 'POST'])
@login_required
def api_set_highlight_keywords():
    if request.method == 'GET':
        return redirect(url_for('project_editor'))
        
    project_id = request.cookies.get('project_id')
    if project_id is None or project_id == '':
        flash('Set working project first')
        return redirect(url_for('project.mylist'))

    raw_hk_inc = request.form.get('form_textarea_inclusion_keywords')
    raw_hk_exc = request.form.get('form_textarea_exclusion_keywords')

    # remove blank
    raw_hk_inc = raw_hk_inc.strip()
    raw_hk_exc = raw_hk_exc.strip()

    # split
    hk_incs = raw_hk_inc.split('\n')
    hk_excs = raw_hk_exc.split('\n')

    # remove empty
    hk_incs_cleaned = []
    for hk_inc in hk_incs:
        hk_inc = hk_inc.strip()
        if hk_inc == '':
            pass
        else:
            hk_incs_cleaned.append(hk_inc)
    
    hk_excs_cleaned = []
    for hk_exc in hk_excs:
        hk_exc = hk_exc.strip()
        if hk_exc == '':
            pass
        else:
            hk_excs_cleaned.append(hk_exc)

    highlight_keywords = {
        "inclusion": hk_incs_cleaned,
        "exclusion": hk_excs_cleaned
    }
    # update
    is_success, project = dora.set_project_highlight_keywords(
        project_id, highlight_keywords
    )

    flash('Saved %s + %s highlight_keywords!' % (
        len(highlight_keywords['inclusion']), 
        len(highlight_keywords['exclusion']), 
    ))
    return redirect(url_for('project.editor', _anchor="ie_keywords_info"))


@bp.route('/api/set_tags', methods=['GET', 'POST'])
@login_required
def api_set_tags():
    if request.method == 'GET':
        return redirect(url_for('project_editor'))
        
    project_id = request.cookies.get('project_id')
    if project_id is None or project_id == '':
        flash('Set working project first')
        return redirect(url_for('project.mylist'))

    raw_tags = request.form.get('form_textarea_tags')

    # remove blank
    tags = raw_tags.strip()

    # split
    tags = tags.split('\n')

    # remove empty
    tags_cleaned = []
    for tag in tags:
        tag = tag.strip()
        if tag == '':
            pass
        else:
            tags_cleaned.append(tag)

    # update
    is_success, project = dora.set_project_tags(project_id, tags_cleaned)

    flash('Saved %s tags!' % (len(tags_cleaned)) )
    return redirect(url_for('project.editor', _anchor="tag_info"))


@bp.route('/api/set_pdf_keywords', methods=['GET', 'POST'])
@login_required
def api_set_pdf_keywords():
    if request.method == 'GET':
        return redirect(url_for('project_editor'))
        
    project_id = request.cookies.get('project_id')
    if project_id is None or project_id == '':
        flash('Set working project first')
        return redirect(url_for('project.mylist'))

    raw_txt = request.form.get('form_textarea_pdf_keywords')

    # remove blank
    lines = raw_txt.strip()

    # split
    keywords = lines.split('\n')

    # remove empty
    keywords_cleaned = []
    for txt in keywords:
        txt = txt.strip()
        if txt == '':
            pass
        else:
            keywords_cleaned.append(txt)

    # update
    is_success, project = dora.set_project_pdf_keywords(project_id, keywords_cleaned)

    flash('Saved %s PDF keywords!' % (len(keywords_cleaned)) )
    return redirect(url_for('project.editor', _anchor="pdf_keywords"))


@bp.route('/api/set_settings', methods=['GET', 'POST'])
@login_required
def api_set_settings():
    '''
    Set the project settings directly

    CAUTION! this function is VERY VERY dangerous.
    Don't use unless you are 120% sure what you are doing.
    '''
    if request.method == 'GET':
        return redirect(url_for('project_editor'))
        
    project_id = request.cookies.get('project_id')
    if project_id is None or project_id == '':
        flash('Set working project first')
        return redirect(url_for('project.mylist'))

    raw_txt = request.form.get('form_textarea_settings')

    # convert to JSON
    try:
        new_prj_settings = json.loads(raw_txt)

    except Exception as err:
        flash('ERROR! Invalid JSON format settings')
        return redirect(url_for('project.editor'))

    # update
    is_success, project = dora.set_project_settings(
        project_id, new_prj_settings
    )

    # then, due to this large update
    # we also need to check and update other things related to setting
    # 1. update the ss_cq based the cq
    # this is based on the decision of 
    srv_project.update_project_papers_ss_cq_by_keystr(
        project.keystr,
        settings.PAPER_SS_EX_SS_CQ_DECISION_NO
    )

    # 2. I'm not sure yet.

    flash('Saved new settings')
    return redirect(url_for('project.editor', _anchor="advanced_mode"))