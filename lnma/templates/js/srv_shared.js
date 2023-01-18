/**
 * This is a shared service for all modules.
 */

var srv_shared = {
    // a dictionary for labels
    label_dict: {
        'pwma': 'Pairwise MA',
        'subg': 'Sub-group MA',
        'nma': 'Network MA',
        'itable': 'Interactive Table'
    },

    regex_pmid: /^\d{6,8}$/,
    is_valid_pmid: function(pmid) {
        return this.regex_pmid.test(pmid);
    },

    get_ds_name_by_pid_and_type: function(pid, pid_type) {
        var _pid_type = pid_type.toLocaleLowerCase();
        var ds_name = 'other';

        if (_pid_type.indexOf('medline')>=0 ||
            _pid_type.indexOf('pmid')>=0 ||
            _pid_type.indexOf('nlm')>=0 ||
            _pid_type.indexOf('pubmed')>=0
        ) {
            ds_name = 'pmid';

        } else if (this.is_valid_pmid(pid)) {
            ds_name = 'pmid';

        } else if (_pid_type.indexOf('md5')>=0) {
            ds_name = 'md5';

        } else if (_pid_type.indexOf('embase')>=0 || 
                   _pid_type.indexOf('ebase')>=0) {
            ds_name = 'embase';
            
        } else if (_pid_type.indexOf('doi')>=0) {
            ds_name = 'doi';
            
        } else {
            ds_name = 'other';
        }

        return ds_name;
    },

    get_paper_pmid_if_exists: function(paper) {
        if (paper.meta.hasOwnProperty('ds_id')) {
            if (paper.meta.ds_id.hasOwnProperty('pmid')) {
                // great, this paper has pmid
                return {
                    type: 'pmid',
                    id: paper.meta.ds_id.pmid
                };
            }
        }
        // oh, this paper has no ds_id or not pmid
        // then just just check return the pid
        return {
            type: this.get_ds_name_by_pid_and_type(
                paper.pid,
                paper.pid_type
            ),
            id: paper.pid
        };
    },

    /**
     * Update the labels by project setting object
     * 
     * @param {Object} settings The settings object of a project
     */
    update_labels_by_project_settings: function(settings) {
        if (settings.hasOwnProperty('outcomes_enabled')) {
            for (let i = 0; i < settings.outcomes_enabled.length; i++) {
                const oc_type = settings.outcomes_enabled[i];
                if (settings.hasOwnProperty('outcome') &&
                    settings.outcome.hasOwnProperty(oc_type)) {
                    for (let i = 0; i < settings.outcome[oc_type].analysis_groups.length; i++) {
                        const d = settings.outcome[oc_type].analysis_groups[i];
                        // put this group name to dictionary
                        this.label_dict[d.abbr] = d.name;
                    }
                }
            }
        }
        
    },

    /**
     * Get the label of a given value
     * 
     * @param {string} v abbr or id
     */
    _lbl: function(v) {
        if (this.label_dict.hasOwnProperty(v)) {
            return this.label_dict[v];
        } else {
            return v;
        }
    },

    /**
     * Create an extract tree
     * the extract tree is a tree-shape data structure
        {
            itable: {},
            pwma: {
                _is_shown: true/false,
                groups: {
                    group1: {
                        _is_shown: true/false,
                        cates: {
                            cate1: {
                                _is_shown: true/false,
                                ocs: {
                                    oc1: {},
                                    oc2: {}
                                }
                            },
                            cate2: {}
                        },
                    },
                    group2: {}
                }
            },
            subg: {},
            nma: {},
        }

        The first level is the oc_type.
        The second level is the group.
        The third level is the cate.
        In each cate, there are outcomes as list.
     * 
     * @param extracts A list of extract JSON object
     * @returns A tree structured extracts
     */
    create_extract_tree: function(extracts) {
        var extract_tree = {};

        for (let i = 0; i < extracts.length; i++) {
            const ext = extracts[i];
            
            var oc_type = ext.oc_type;
            var group = ext.meta.group;
            var cate = ext.meta.category;

            if (ext.oc_type == 'itable') {
                // the side effect is that if there are multiple exts(itables),
                // the last one (randomly) will overwrite all others.
                // BUT!!! there should be only one itable for each cq in project
                extract_tree.itable = ext;

            } else {
                // check the type
                if (!extract_tree.hasOwnProperty(oc_type)) {
                    extract_tree[oc_type] = {
                        _is_shown: true,
                        groups: {}
                    }
                }

                // check the group
                if (!extract_tree[oc_type].groups.hasOwnProperty(group)) {
                    extract_tree[oc_type].groups[group] = {
                        _is_shown: true,
                        cates: {}
                    };
                }

                // check the cate
                if (!extract_tree[oc_type].groups[group].cates.hasOwnProperty(cate)) {
                    extract_tree[oc_type].groups[group].cates[cate] = {
                        _is_shown: true,
                        ocs: {}
                    }
                }
                // put this outcome to the cate
                extract_tree[oc_type].groups[group].cates[cate].ocs[ext.abbr] = ext;
            }
        }

        return extract_tree;
    },


    /**
     * Create a sorted extract tree
     *  the extract tree is a tree-shape data structure
        [{
            oc_type: pwma,
            _is_shown: true/false,
            groups: [{
                abbr: primary,
                _is_shown: true/false,
                cates: [{
                    name: cate_name,                    
                    _is_shown: true/false,
                    ocs: [{}, {}]
                }, {}]
            },
            group2: []

        }, {}
        ]

        The first level is the oc_type.
        The second level is the group.
        The third level is the cate.
        In each cate, there are outcomes as list.
     * 
     * @param extract_tree An extract_tree
     * @returns A sorted tree structured extracts
     */
    create_extract_tree_sorted: function(extract_tree, flag_use_jarvis_oc_order) {
        if (typeof(flag_use_jarvis_oc_order)=='undefined') {
            flag_use_jarvis_oc_order = false;
        }
        var sorted = [];

        var oc_types = Object.keys(extract_tree).sort();

        for (let i = 0; i < oc_types.length; i++) {
            const oc_type = oc_types[i];

            if (oc_type == 'itable') {
                // sorted.push({
                //     oc_type: oc_type,
                //     oc: extract_tree[oc_type]
                // });
                continue;
            }
            
            var groups = Object.keys(extract_tree[oc_type].groups).sort();
            var sorted_groups = [];
            for (let j = 0; j < groups.length; j++) {
                const group = groups[j];
                
                var cates = Object.keys(extract_tree[oc_type].groups[group].cates).sort();
                var sorted_cates = [];
                for (let k = 0; k < cates.length; k++) {
                    const cate = cates[k];
                    
                    // now, check the ocs
                    var ocs = extract_tree[oc_type].groups[group].cates[cate].ocs;
                    var ocs_list = Object.keys(ocs).map(function(abbr) {
                        // for sorting
                        ocs[abbr].oc_full_name = ocs[abbr].meta.full_name;
                        return ocs[abbr];
                    });

                    if (flag_use_jarvis_oc_order) {
                        // for this case, the order is not empty
                        ocs_list.sort(jarvis.compare_oc_names);

                    } else {
                        // just use alphabet
                        ocs_list.sort(function(a, b) {
                            return a.meta.full_name > b.meta.full_name ? 1 : -1;
                        });
                    }
                    
                    var sorted_cate = {
                        name: cate,
                        ocs: ocs_list
                    };
                    sorted_cates.push(sorted_cate);
                }
                
                var sorted_group = {
                    abbr: group,
                    cates: sorted_cates
                };
                sorted_groups.push(sorted_group);
            }

            var sorted_oc_type = {
                oc_type: oc_type,
                groups: sorted_groups
            };
            sorted.push(sorted_oc_type);
        }

        return sorted;
    },


    /**
     * Create an extract dictionary
     * 
     * @param {Array} extracts A list of extract JSON objects
     * @returns a dictionary for extracts based on abbr
     */
    create_extract_dict: function(extracts) {
        var extract_dict = {};
        for (let i = 0; i < extracts.length; i++) {
            var extract = extracts[i];
            var abbr = extract.abbr;
            
            extract_dict[abbr] = extract;
        }
    
        // update the vpp data
        return extract_dict;
    },
    
    /**
     * Get the rounded number
     * @param {float} v 
     * @returns float rounded number
     */
    _round2: function(v) {
        return (Math.round(v * 100) / 100).toFixed(2);
    },

    /**
     * Get the certainty of evidence color
     * @param {string} which_is_better lower / higher
     * @param {float} te Treatment effect
     * @param {float} lw lower CI
     * @param {float} up upper CI
     * @param {string} cie 
     * @returns {string} the color class
     */
    get_ce_color: function(which_is_better, te, lw, up, cie) {
        // use the two digits rounded value instead of the real value
        var sm = parseFloat(this._round2(te));
        var lower = parseFloat(this._round2(lw));
        var upper = parseFloat(this._round2(up));

        var delta_sm = Math.abs(1 - sm);
        var is_ci_cross_one = lower <= 1 && upper >= 1;
        var ci_diff = upper - lower;

        var _d2c = function(wib, sm, cie) {
            if (sm == 1) { return 'cie-nner-' + cie; }
            if (wib == 'lower') {
                if (sm < 1) { return 'cie-bene-' + cie; }
                else { return 'cie-harm-' + cie; }
            } else {
                if (sm > 1) { return 'cie-bene-' + cie; }
                else { return 'cie-harm-' + cie; }
            }
        }

        /**
         * 2021-03-28: update the rule for color
            1. if sm = 1 -> grey
            2. if sm not = 1 then:
                a. if CI not cross -> red / green depends on direction of sm
                b. if CI cross 1 then:
                    i. if the difference between upper and lower < 0.3, then
                        1. if the 1- sm =<0.1 -> grey
                        2. if the 1- sm >0.1 -> depends on direction of sm
                    ii. if the difference between upper and lower >= 0.3, then
                        1. depends upon direction of sm
            */

        // Rule 1
        if (sm == 1) {
            return 'cie-nner-' + cie;
        }

        // small is green, big is red
        if (is_ci_cross_one) {
            // Rule 2b
            if (ci_diff < 0.3) {
                // Rule 2bi
                if (delta_sm <= 0.1) {
                    return 'cie-nner-' + cie; 
                } else {
                    return _d2c(which_is_better, sm, cie);
                }
            } else {
                // Rule 2bii
                return _d2c(which_is_better, sm, cie);
            }
        } else {
            // Rule 2a
            return _d2c(which_is_better, sm, cie);
        }

    },

    /**
     * Get the rs and cfg for analyzer
     * 
     * @param {object} extract an Extract object
     */
    get_rs_cfg_from_extract: function(extract, rs_type) {
        if (typeof(rs_type) == 'undefined') {
            rs_type = 'main'
        }

        // prepare th
        var rs = [];
        var cfg = {};


    },

    /*************************************************
     * Helpers
     *************************************************/

    get_int: function(v) {
        try {
            var intv = parseInt(v);
            return intv;
        } catch {
            return null;
        }
    },

    get_str: function(v) {
        try {
            var strv = ""+v;
            return strv;
        } catch {
            return '';
        }
    },

    get_year: function(s) {
        const regex = /\d{4}/gm;
        let m;
        if ((m = regex.exec(s)) !== null) {
            return m[0];
        }
        return '';
    },

    get_first_author: function(s) {
        var aus = s.split(';');
        if (aus.length == 1) {
            aus = s.split(',');
        }
        return aus[0];
    },

    isna: function(v) {
        if (v == null) {
            return true;
        } else if (isNaN(v)) {
            return true;
        } else if (v === '') {
            return true;
        } else if ((''+v).toLocaleUpperCase() === 'NA') {
            return true;
        } else if (v == '-') {
            return true;
        } else {
            return false;
        }
    },
};