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
        get_extract: "[[ url_for('extractor.get_extract') ]]",
        get_extracts: "[[ url_for('extractor.get_extracts') ]]",
        get_extract_and_papers: "[[ url_for('extractor.get_extract_and_papers') ]]",

        get_included_papers_and_selections: "[[ url_for('extractor.get_included_papers_and_selections') ]]",
        update_paper_selections: "[[ url_for('extractor.update_paper_selections') ]]",

        extract_data: "[[ url_for('extractor.extract_data') ]]"
    },

    goto_extract_data: function(abbr) {
        location.href = this.url.extract_data + '?abbr=' + abbr;
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

    get_extract: function(project_id, abbr, callback) {
        $.get(
            this.url.get_extract,
            {
                project_id: project_id,
                abbr: abbr,
                rnd: Math.random()
            },
            callback,
            'json'
        );
    },

    get_extracts: function(project_id, callback) {
        $.get(
            this.url.get_extracts,
            {
                project_id: project_id,
                rnd: Math.random()
            },
            callback,
            'json'
        );
    },

    get_included_papers_and_selections: function(project_id, callback) {
        $.ajax({
            type: 'GET',
            dataType: "json",
            url: this.url.get_included_papers_and_selections,
            data: {
                rnd: Math.random(),
                project_id: project_id
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when getting included papers', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    get_extract_and_papers: function(project_id, abbr, callback) {
        $.ajax({
            type: 'GET',
            dataType: "json",
            url: this.url.get_extract_and_papers,
            data: {
                project_id: project_id,
                abbr: abbr,
                rnd: Math.random()
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when getting included papers', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    update_paper_selections: function(project_id, pid, abbrs, callback) {
        $.ajax({
            type: 'POST',
            dataType: "json",
            url: this.url.update_paper_selections,
            data: {
                rnd: Math.random(),
                project_id: project_id,
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

    // the project is binded when running extracting
    project: null,

    tpl: {
        oc_type: {
            pwma: {
                default: {
                    abbr: '',
                    oc_type: 'pwma',
                    category: 'default',
                    group: 'primary',
                    full_name: 'pwma Outcome full name',
                    included_in_plots: 'yes',
                    included_in_sof: 'yes',
                    input_format: 'PRIM_CAT_RAW',
                    measure_of_effect: 'RR',
                    fixed_or_random: 'fixed',
                    which_is_better: 'lower',

                    "pooling_method": "Inverse",
                    "tau_estimation_method": "DL",
                    "hakn_adjustment": "no",
                    "smd_estimation_method": "Hedges",
                    "prediction_interval": "no",
                    "sensitivity_analysis": "no",
                    "cumulative_meta_analysis": "no",
                    "cumulative_meta_analysis_sortby": "year",

                    attrs: null,
                    cate_attrs: null
                },
            },
            subg: {
                default: {
                    abbr: '',
                    subgroups: ['A', 'B'],
                    oc_type: 'subg',
                    category: 'default',
                    group: 'subgroup',
                    full_name: 'pwma Outcome full name',
                    included_in_plots: 'yes',
                    included_in_sof: 'yes',
                    input_format: 'SUBG_CAT_RAW',
                    measure_of_effect: 'RR',
                    fixed_or_random: 'fixed',
                    which_is_better: 'lower',
                    attrs: [ "Et", "Nt", "Ec", "Nc" ],
                    treatment: {
                        abbr: "Treat",
                        full_name: "Treatment arm full name"
                    },
                    control: {
                        abbr: "Ctrl",
                        full_name: "Control arm full name"
                    }
                }
            },
            nma: {
                default: {
                    abbr: '',
                    oc_type: 'nma',
                    category: 'default',
                    group: 'primary',
                    full_name: 'NMA Outcome full name',
                    included_in_plots: 'yes',
                    included_in_sof: 'yes',
                    included_in_em: 'yes',
                    input_format: 'raw',
                    measure_of_effect: 'HR',
                    method: 'freq',
                    fixed_or_random: 'fixed',
                    which_is_better: 'lower',
                    attrs: ['t1', 't2', 
                        'event_t1', 'total_t1', 
                        'event_t2', 'total_t2'],
                    treatment: {
                        treat_abbr: {
                            abbr: 'treatAbbr',
                            full_name: "Treatment full name"
                        }
                    }
                }
            },
            itable: [[ config['settings']['OC_TYPE_TPL']['itable']|tojson ]]
        },
        input_format: {
            pwma: {
                // PRIM_CAT_RAWp: ['Et', 'Nt', 'Ec', 'Nc', 'treatment', 'control'],
                // PRIM_CAT_PREp: ['TE', 'lowerci', 'upperci'],
                // PRIM_CONTD_RAWp: ['Nt', 'Mt', 'SDt', 'Nc', 'Mc', 'SDc'],
                // PRIM_CONTD_PREp: ['TE', 'SE'],
                // PRIM_CATIRR_RAWp: ['Et', 'Tt', 'Ec', 'Tc'],
                // PRIM_CAT_RAW_G5p: ['GA_Et', 'GA_Nt', 'GA_Ec', 'GA_Nc', 
                //     'G34_Et', 'G34_Ec', 'G3H_Et', 'G3H_Ec', 'G5N_Et', 'G5N_Ec', 
                //     'drug_used', 'malignancy'],

                PRIM_CAT_RAW: [{
                    'abbr': 'PRIM_CAT_RAW_treat',
                    'name': 'Treatment Arm',
                    'attrs': [{
                        'abbr': 'Et',
                        'name': 'Event',
                        'subs': null
                    }, {
                        'abbr': 'Nt',
                        'name': 'Total',
                        'subs': null
                    }, {
                        'abbr': 'treatment',
                        'name': 'Treatment',
                        'subs': null
                    }]
                }, {
                    'abbr': 'PRIM_CAT_RAW_control',
                    'name': 'Control Arm',
                    'attrs': [{
                        'abbr': 'Ec',
                        'name': 'Event',
                        'subs': null
                    }, {
                        'abbr': 'Nc',
                        'name': 'Total',
                        'subs': null
                    }, {
                        'abbr': 'control',
                        'name': 'Control',
                        'subs': null
                    }]
                }],

                PRIM_CAT_PRE: [{
                    'abbr': 'PRIM_CAT_PRE_default', 
                    'name': 'Default attributes', 
                    'attrs': [{
                        'abbr': 'TE', 
                        'name': 'TE',
                        'subs': null,
                    }, {
                        'abbr': 'lowerci', 
                        'name': 'Lower CI', 
                        'subs': null,
                    }, {
                        'abbr': 'upperci', 
                        'name': 'Upper CI', 
                        'subs': null,
                    }]
                }],

                PRIM_CONTD_RAW: [{
                    'abbr': 'PRIM_CONTD_RAW_treat', 
                    'name': 'Treatment Arm', 
                    'attrs': [{
                        'abbr': 'Nt', 
                        'name': 'Nt',
                        'subs': null,
                    }, {
                        'abbr': 'Mt', 
                        'name': 'Mt', 
                        'subs': null,
                    }, {
                        'abbr': 'SDt', 
                        'name': 'SDt', 
                        'subs': null,
                    }]
                }, {
                    'abbr': 'PRIM_CONTD_RAW_control', 
                    'name': 'Control Arm', 
                    'attrs': [{
                        'abbr': 'Nc', 
                        'name': 'Nc',
                        'subs': null,
                    }, {
                        'abbr': 'Mc', 
                        'name': 'Mc', 
                        'subs': null,
                    }, {
                        'abbr': 'SDc', 
                        'name': 'SDc', 
                        'subs': null,
                    }]
                }],

                PRIM_CONTD_PRE: [{
                    'abbr': 'PRIM_CONTD_PRE_default', 
                    'name': 'Default attributes', 
                    'attrs': [{
                        'abbr': 'TE', 
                        'name': 'TE',
                        'subs': null,
                    }, {
                        'abbr': 'SE',
                        'name': 'SE', 
                        'subs': null,
                    }]
                }],

                PRIM_CATIRR_RAW: [{
                    'abbr': 'PRIM_CATIRR_RAW_default', 
                    'name': 'Default attributes', 
                    'attrs': [{
                        'abbr': 'Et', 
                        'name': 'Et',
                        'subs': null,
                    }, {
                        'abbr': 'Tt',
                        'name': 'Tt', 
                        'subs': null,
                    }, {
                        'abbr': 'Ec', 
                        'name': 'Ec',
                        'subs': null,
                    }, {
                        'abbr': 'Tc',
                        'name': 'Tc', 
                        'subs': null,
                    }]
                }],

                PRIM_CAT_RAW_G5: [{
                    'abbr': 'default',
                    'name': 'Treatments',
                    'attrs': [{
                        'abbr': 'drug_used',
                        'name': 'Drug Used',
                        'subs': null
                    }, {
                        'abbr': 'malignancy',
                        'name': 'Malignancy',
                        'subs': null
                    }]
                },{
                    'abbr': 'GA',
                    'name': 'All Grade',
                    'attrs': [{
                        'abbr': 'GA_Et',
                        'name': 'Tx',
                        'subs': null
                    }, {
                        'abbr': 'GA_Nt',
                        'name': 'N',
                        'subs': null
                    }, {
                        'abbr': 'GA_Ec',
                        'name': 'Control',
                        'subs': null
                    }, {
                        'abbr': 'GA_Nc',
                        'name': 'n',
                        'subs': null
                    }]
                }, {
                    'abbr': 'G34',
                    'name': 'Grade 3/4',
                    'attrs': [{
                        'abbr': 'G34_Et',
                        'name': 'Tx',
                        'subs': null
                    }, {
                        'abbr': 'G34_Nt',
                        'name': 'Control',
                        'subs': null
                    }]
                }, {
                    'abbr': 'G3H',
                    'name': 'Grade 3 or higher',
                    'attrs': [{
                        'abbr': 'G3H_Et',
                        'name': 'Tx',
                        'subs': null
                    }, {
                        'abbr': 'G3H_Nt',
                        'name': 'Control',
                        'subs': null
                    }]
                }, {
                    'abbr': 'G5N',
                    'name': 'Grade 5 only',
                    'attrs': [{
                        'abbr': 'G5N_Et',
                        'name': 'Tx',
                        'subs': null
                    }, {
                        'abbr': 'G5N_Nt',
                        'name': 'Control',
                        'subs': null
                    }]
                }]
            },
            subg: {
                SUBG_CATIRR_RAW: ['Et', 'Tt', 'Ec', 'Tc'],
                SUBG_CAT_RAW: ['Et', 'Nt', 'Ec', 'Nc'],
                SUBG_CAT_PRE: ['TE', 'lowerci', 'upperci'],
                SUBG_CONTD_RAW: ['Nt', 'Nt', 'SDt', 'Nc', 'Mc', 'SDc'],
                SUBG_CONTD_PRE: ['TE', 'SE'],
            },
            nma: {
                raw: ['t1', 't2', 'event_t1', 'total_t1', 'event_t2', 'total_t2'],
                pre: ['t1', 't2', 'sm', 'lowerci', 'upperci', 
                      'survival_t1', 'survival_t2',
                      'Ec_t1', 'Et_t1', 'Ec_t2', 'Et_t2']
            }
        },

        filter: {
            display_name: '',
            type: 'radio',
            attr: null,
            value: 0,
            values: [{
                display_name: 'All',
                value: 0,
                sql_cond: "{$col} is not NULL",
                default: true
            }]
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
        d.attrs.main = this.mk_oc_data_attr(oc);

        return d;
    },

    /**
     * Make the empty attrs
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
    }
};
