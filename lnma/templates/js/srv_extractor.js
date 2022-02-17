/**
 * Service Extractor
 * 
 * This is a service agent for using extractor services
 */

var srv_extractor = {

    // all urls for extractor
    url: {
        create_extract: "[[ url_for('extractor.create_extract') ]]",
        update_extract: "[[ url_for('extractor.update_extract') ]]",
        update_extract_meta: "[[ url_for('extractor.update_extract_meta') ]]",
        update_extract_data: "[[ url_for('extractor.update_extract_data') ]]",
        update_extract_incr_data: "[[ url_for('extractor.update_extract_incr_data') ]]",

        copy_extract: "[[ url_for('extractor.copy_extract') ]]",
        delete_extract: "[[ url_for('extractor.delete_extract') ]]",

        get_paper: "[[ url_for('extractor.get_paper') ]]",
        get_pdata_in_extract: "[[ url_for('extractor.get_pdata_in_extract') ]]",
        get_pdata_in_itable: "[[ url_for('extractor.get_pdata_in_itable') ]]",
        get_itable: "[[ url_for('extractor.get_itable') ]]",
        get_extract: "[[ url_for('extractor.get_extract') ]]",
        get_extracts: "[[ url_for('extractor.get_extracts') ]]",
        get_extract_and_papers: "[[ url_for('extractor.get_extract_and_papers') ]]",

        get_included_papers_and_selections: "[[ url_for('extractor.get_included_papers_and_selections') ]]",
        update_paper_one_selection: "[[ url_for('extractor.update_paper_one_selection') ]]",
        update_paper_selections: "[[ url_for('extractor.update_paper_selections') ]]",

        extract_by_paper: "[[ url_for('extractor.extract_by_paper') ]]",
        extract_by_outcome: "[[ url_for('extractor.extract_by_outcome') ]]",

        sort_rct_seq: "[[ url_for('extractor.sort_rct_seq') ]]",
        manage_outcomes: "[[ url_for('extractor.manage_outcomes') ]]",
    },

    // the project is binded when running extracting
    project: null,

    // the default templates for 
    tpl: {
        oc_type: [[ config['settings']['OC_TYPE_TPL']|tojson ]],
        input_format: [[ config['settings']['INPUT_FORMAT_TPL']|tojson ]],
        filter: [[ config['settings']['FILTER_TPL']|tojson ]]
    },

    // the settings
    setting: {
        input_size: {
            min: [[ config['settings']['EXTRACTOR_INPUT_BOX_MIN_SIZE'] ]],
            max: [[ config['settings']['EXTRACTOR_INPUT_BOX_MAX_SIZE'] ]]
        }
    },

    sort_rct_seq: function(callback) {
        $.ajax({
            url: this.url.sort_rct_seq,
            type: 'get',
            dataType: 'json',
            data: { rnd: Math.random() },
            success: callback,
            error: function(data) {
                toast('System error when updating the studies, please try later.', 'error');
            }
        })
    },

    goto_extract_by_outcome: function(abbr) {
        location.href = this.url.extract_by_outcome + '?abbr=' + abbr;
    },

    create_extract: function(project_id, oc_type, abbr, meta, data, callback) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: this.url.create_extract,
            data: {
                project_id: project_id, 
                oc_type: oc_type, 
                abbr:abbr,
                meta:JSON.stringify(meta), 
                data:JSON.stringify(data)
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when creating the extraction.', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    update_extract: function(
        project_id,
        oc_type,
        abbr,
        meta,
        data,
        callback
    ) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: this.url.update_extract,
            data: {
                project_id:project_id, 
                oc_type:oc_type, 
                abbr:abbr,
                meta:JSON.stringify(meta), 
                data:JSON.stringify(data)
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when saving the extraction.', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    update_extract_meta: function(
        project_id,
        oc_type,
        abbr,
        meta,
        callback
    ) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: this.url.update_extract_meta,
            data: {
                project_id:project_id, 
                oc_type:oc_type, 
                abbr:abbr,
                meta:JSON.stringify(meta)
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when saving the extraction.', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    update_extract_incr_data: function(
        project_id,
        oc_type,
        abbr,
        data,
        callback
    ) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: this.url.update_extract_incr_data,
            data: {
                project_id:project_id, 
                oc_type:oc_type, 
                abbr:abbr,
                data:JSON.stringify(data)
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when saving the updated data.', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    get_paper: function(pid, callback) {
        $.ajax({
            type: 'GET',
            dataType: "json",
            url: this.url.get_paper,
            data: {
                pid: pid,
                rnd: Math.random(),
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when getting included papers', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    get_pdata_in_extract: function(project_id, abbr, pid, callback) {
        $.get(
            this.url.get_pdata_in_extract,
            {
                project_id: project_id,
                abbr: abbr,
                pid: pid,
                rnd: Math.random()
            },
            callback,
            'json'
        );
    },

    get_pdata_in_itable: function(project_id, cq_abbr, pid, callback) {
        $.get(
            this.url.get_pdata_in_itable,
            {
                project_id: project_id,
                cq_abbr: cq_abbr,
                pid: pid,
                rnd: Math.random()
            },
            callback,
            'json'
        );
    },

    get_itable: function(project_id, cq_abbr, callback) {
        $.get(
            this.url.get_itable,
            {
                project_id: project_id,
                cq_abbr: cq_abbr,
                rnd: Math.random()
            },
            callback,
            'json'
        );
    },

    get_extract: function(project_id, cq_abbr, abbr, callback) {
        $.get(
            this.url.get_extract,
            {
                project_id: project_id,
                cq_abbr: cq_abbr,
                abbr: abbr,
                rnd: Math.random()
            },
            callback,
            'json'
        );
    },

    get_extracts: function(project_id, cq_abbr, callback) {
        $.get(
            this.url.get_extracts,
            {
                project_id: project_id,
                cq_abbr: cq_abbr,
                rnd: Math.random()
            },
            callback,
            'json'
        );
    },

    get_included_papers_and_selections: function(project_id, cq_abbr, callback) {
        $.ajax({
            type: 'GET',
            dataType: "json",
            url: this.url.get_included_papers_and_selections,
            data: {
                project_id: project_id,
                cq_abbr: cq_abbr,
                rnd: Math.random(),
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when getting included papers', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    get_extract_and_papers: function(project_id, cq_abbr, abbr, callback) {
        $.ajax({
            type: 'GET',
            dataType: "json",
            url: this.url.get_extract_and_papers,
            data: {
                project_id: project_id,
                cq_abbr: cq_abbr,
                abbr: abbr,
                rnd: Math.random()
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when setting paper selections', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    update_paper_one_selection: function(project_id, pid, abbr, is_selected, callback) {
        $.ajax({
            type: 'POST',
            dataType: "json",
            url: this.url.update_paper_one_selection,
            data: {
                rnd: Math.random(),
                project_id: project_id,
                pid: pid,
                abbr: abbr,
                is_selected: is_selected
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when setting selection', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    update_paper_selections: function(project_id, cq_abbr, pid, abbrs, callback) {
        $.ajax({
            type: 'POST',
            dataType: "json",
            url: this.url.update_paper_selections,
            data: {
                rnd: Math.random(),
                project_id: project_id,
                cq_abbr: cq_abbr,
                pid: pid,
                abbrs: abbrs
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when getting included papers', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    ///////////////////////////////////////////////////////////////////////////
    // Utils for extractor
    ///////////////////////////////////////////////////////////////////////////

    get_input_size: function(str) {
        // convert null to empty
        if (typeof(str) == 'undefined' || str == null) {
            str = '';
        }
        // convert number to string
        str = '' + str;
        var s = str.length;
        if (s < this.setting.input_size.min) {
            return this.setting.input_size.min;
        } else if (s > this.setting.input_size.max) {
            return this.setting.input_size.max;
        } else {
            return s;
        }
    },

    /**
     * Make the oc abbr for an outcome / ae
     */
    mk_oc_abbr: function() {
        var result = '';
        var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        var len = characters.length;
        for (var i = 0; i < 8; i++) {
            result += characters.charAt(Math.floor(Math.random() * len));
        }
        return result;
    },

    /**
     * Make the column abbr / id for itable
     */
    mk_it_abbr: function() {
        var result = '';
        var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        var len = characters.length;
        for (var i = 0; i < 12; i++) {
            result += characters.charAt(Math.floor(Math.random() * len));
        }
        return result;
    },

    /**
     * Make the empty extraction data for a paper
     */
    mk_oc_data: function(oc, is_selected, is_checked) {
        if (typeof(is_selected) == 'undefined') {
            is_selected = false;
        }
        if (typeof(is_checked) == 'undefined') {
            is_checked = true;
        }
        
        // create an empty item
        var d = {
            is_selected: is_selected,
            is_checked: is_checked,
            n_arms: 2,
            attrs: {
                main: {},
                other: []
            }
        };
        
        // fill the main track of the oc extraction.
        d.attrs.main['g0'] = this.mk_oc_data_attr(oc);

        // 2022-02-16: fix the subgroup bug
        if (oc.meta.group == 'subgroup') {
            for (let i = 1; i < oc.meta.sub_groups.length; i++) {
                d.attrs.main['g' + i] = this.mk_oc_data_attr(oc);
            }
        }

        return d;
    },

    fix_oc_data_attr: function(d, oc) {
        for (let subg_idx = 0; subg_idx < oc.meta.sub_groups.length; subg_idx++) {
            // check main
            if (d.attrs.main.hasOwnProperty('g' + subg_idx)) {
                // just fix
                d.attrs.main['g' + subg_idx] = this.fix_arm_data_attr(
                    d.attrs.main['g' + subg_idx],
                    oc
                );
            } else {
                // oh, it's missing, then add
                d.attrs.main['g' + subg_idx] = this.mk_oc_data_attr(oc);
            }

            // check other arms
            for (let arm_idx = 0; arm_idx < d.attrs.other.length; arm_idx++) {
                if (d.attrs.other[arm_idx].hasOwnProperty('g' + subg_idx)) {
                    // just fix
                    d.attrs.other[arm_idx]['g' + subg_idx] = this.fix_arm_data_attr(
                        d.attrs.other[arm_idx]['g' + subg_idx],
                        oc
                    );
                } else {
                    // oh, it's missing, then add
                    d.attrs.other[arm_idx]['g' + subg_idx] = this.mk_oc_data_attr(oc);
                }
                
            }
            
        }
        return d;
    },

    fix_arm_data_attr: function(arm, oc) {
        // check all cate_attr in this oc
        for (let i = 0; i < oc.meta.cate_attrs.length; i++) {
            // check each category
            const cate = oc.meta.cate_attrs[i];
            for (let j = 0; j < cate.attrs.length; j++) {
                // check each attribute
                const attr = cate.attrs[j];
                
                if (attr.subs == null) {
                    if (arm.hasOwnProperty(attr.abbr)) {
                        // ok, it has
                    } else {
                        arm[attr.abbr] = ''
                    }

                } else {
                    // check each sub in the attribute
                    for (let k = 0; k < attr.subs.length; k++) {
                        const sub = attr.subs[k];
                        if (arm.hasOwnProperty(sub.abbr)) {
                            // ok, it has
                        } else {
                            arm[sub.abbr] = ''
                        }
                    }
                }
            }
        }

        return arm;
    },

    /**
     * Make the empty attrs
     * 
     * For the given outcome structure on the subg
     */
    mk_oc_data_attr: function(oc) {
        var d = {};

        for (let i = 0; i < oc.meta.cate_attrs.length; i++) {
            // check each category
            const cate = oc.meta.cate_attrs[i];
            for (let j = 0; j < cate.attrs.length; j++) {
                // check each attribute
                const attr = cate.attrs[j];
                
                if (attr.subs == null) {
                    // if there is no sub, just use this attr
                    d[attr.abbr] = '';

                } else {
                    // check each sub in the attribute
                    for (let k = 0; k < attr.subs.length; k++) {
                        const sub = attr.subs[k];
                        d[sub.abbr] = '';
                    }
                }
            }
        }

        return d;
    },

    /**
     * Set number of arms to a paper_data according to oc meta
     */
    set_n_arms: function(paper_data, n_arms, is_copy_main) {
        // get the is_copy_main default value
        if (typeof(is_copy_main) == 'undefined') {
            is_copy_main = true;
        }

        // fix the data type error
        if (typeof(n_arms)=='string') {
            n_arms = parseInt(n_arms);
        }

        // set the n_arms
        paper_data.n_arms = n_arms;

        // update the others
        var new_n_others = n_arms - 2;
        if (new_n_others == paper_data.attrs.other.length) {
            // which means the number of arms doesn't change

        } else if (new_n_others > paper_data.attrs.other.length) {
            // the number of arms increases, need to put more elements
            var delta = new_n_others - paper_data.attrs.other.length;
            // add each as a new ext
            for (let i = 0; i < delta; i++) {
                // just copy the keys from main track
                var obj = JSON.parse(JSON.stringify(paper_data.attrs.main));
                if (is_copy_main) {
                    // nothing to do when copy main

                } else {
                    // clear
                    for (const key in obj) {
                        if (Object.hasOwnProperty.call(obj, key)) {
                            obj[key] = '';
                        }
                    }
                }
                paper_data.attrs.other.push(obj);
            }

        } else {
            // the number of arms decreases, need to remove
            var delta = paper_data.attrs.other.length - new_n_others;
            for (let i = 0; i < delta; i++) {
                paper_data.attrs.other.pop();
            }
        }

        return paper_data;
    },

    /**
     * Create a ATTR NAME -> abbr dictionary
     * 
     * The attribute name is in upper case.
     * 
     * @param {Object} extract an Extract object
     */
    mk_oc_name2abbr_dict: function(extract) {
        var dict = {};
        for (let j = 0; j < extract.meta.cate_attrs.length; j++) {
            const cate = extract.meta.cate_attrs[j];
            for (let k = 0; k < cate.attrs.length; k++) {
                const attr = cate.attrs[k];
                var attr_name = cate.name.toLocaleUpperCase() + '|' + 
                                attr.name.toLocaleUpperCase();
                // check the subs 
                if (attr.subs == null) {
                    // this means this attr has no sub items
                    dict[attr_name] = attr.abbr;
                } else {
                    for (let l = 0; l < attr.subs.length; l++) {
                        const sub = attr.subs[l];
                        var name = attr_name + '|' + sub.name.toLocaleUpperCase();
                        dict[name] = sub.abbr;
                    }
                }
            }
        }
        return dict;
    }
};
