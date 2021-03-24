/**
 * Service Extractor
 * 
 * This is a service agent for using extractor services
 */

var srv_extractor = {

    url: {
        create_extract: "[[ url_for('extractor.create_extract') ]]",
        update_extract: "[[ url_for('extractor.update_extract') ]]",
        update_extract_meta: "[[ url_for('extractor.update_extract_meta') ]]",
        copy_extract: "[[ url_for('extractor.copy_extract') ]]",
        delete_extract: "[[ url_for('extractor.delete_extract') ]]",
        get_paper: "[[ url_for('extractor.get_paper') ]]",
        get_extract: "[[ url_for('extractor.get_extract') ]]",
        get_extracts: "[[ url_for('extractor.get_extracts') ]]",
        get_extract_and_papers: "[[ url_for('extractor.get_extract_and_papers') ]]",

        extract_data: "[[ url_for('extractor.extract_data') ]]"
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
            itable: {
                default: {
                    abbr: 'itable',
                    oc_type: 'itable',
                    category: 'default',
                    group: 'itable',
                    full_name: 'Interactive Table',
                    input_format: 'custom',
                    filters: [{
                        display_name: 'Included in MA',
                        type: 'radio',
                        attr: 'Included in MA',
                        value: 0,
                        values: [{
                            display_name: 'All',
                            value: 0,
                            sql_cond: "{$col} is not NULL",
                            default: true
                        }]
                    }],
                    /**
                     * To make sure the order of the cate and attr list
                     * the attrs are saved as a hierarchical list structure.
                     * As a result, need to implement serval functions
                     */
                    cate_attrs: [
                    {
                        abbr: 'ITABLECAT000',
                        name: "TRIAL CHARACTERISTICS",
                        attrs: [{
                            abbr: 'ITABLEATT000',
                            name: 'Phase',
                            subs: null
                        }]
                    },
                    {
                        abbr: 'ITABLECATSYS',
                        name: "_SYS",
                        attrs: [{
                            abbr: 'ITABLEECATSYS001',
                            name: 'URL',
                            subs: null
                        }, {
                            abbr: 'ITABLEECATSYSSUB002',
                            name: 'Included in MA',
                            subs: null
                        }]
                    }
                    ]
                }
            }
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
};