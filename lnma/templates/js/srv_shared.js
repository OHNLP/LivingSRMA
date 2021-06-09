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
     *  the extract tree is a tree-shape data structure
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
    create_extract_tree_sorted: function(extract_tree) {
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
                        return ocs[abbr];
                    });
                    ocs_list.sort(function(a, b) {
                        return a.meta.full_name > b.meta.full_name ? 1 : -1;
                    });
                    
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


};