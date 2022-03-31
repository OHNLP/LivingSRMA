var vw_studyfilter = {
    vpp: null,
    vpp_id: "#vw_studyfilter",
    blank_val: '%',

    // attrs
    attrs: [{
        display_name: 'ICI Class (Rx)',
        name: 'Class of ICI',
        values: [
            'PD1',
            'PD-L1',
            'CTLA-4'
        ]
    }, {
        display_name: 'ICI Name (Rx)',
        name: 'Name of ICI',
        values: [
            'Atezolizumab',
            'Avelumab',
            'Cemiplimab',
            'Durvalumab',
            'Ipilimumab',
            'Nivolumab',
            'Pembrolizumab',
            'Tremelimumab'
        ]
    }, {
        display_name: 'Type of Therapy (Rx)',
        name: 'Monotherapy/combination',
        values: [
            'Combination',
            'Monotherapy'
        ]
    }, {
        display_name: 'Type of combination (Rx)',
        name: 'Type of combination',
        values: [
            'ICI+ICI',
            'ICI+Chemo',
            'ICI+TKI',
            'ICI+MEKi',
            'ICI+Anti-VEGF',
            'ICI+RadiatICIn',
            'ICI+Vaccine',
            'ICI+BRAFi+MEKi',
            'ICI+Chemo+Anti-VEGF',
            'ICI+ICI+Chemo',
        ]
    }, {
        display_name: 'Control Arm',
        name: 'Type of control',
        values: [
            'Chemo',
            'TKI',
            'Interferon',
            'Multikinase inhibitor',
            'mTOR inhibitor',
            'Radiation',
            'Vaccine',
            'Placebo',
            'Chemo/Anti-EGFR',
            'Chemo+Anti-VEGF',
            'Chemo/TKI',
            'BRAFi+MEKi',
            'Best supportive care'
        ]
    }, {
        display_name: 'Cancer Type',
        name: 'Cancer type',
        values: [
            'Bladder',
            'Breast',
            'Colorectal',
            'Esophageal/GEJ',
            'Gastric/GEJ',
            'Head and Neck ',
            'Hepatocellular',
            'Melanoma',
            'Mesothelioma',
            'Multiple Myeloma',
            'Non-Small Cell Lung',
            'Pancreatic',
            'Prostate',
            'Renal cell',
            'Small Cell Lung',
            'Urothelial'
        ]
    }],

    // the data is for the 
    init: function(data) {

        // create a new list of attrs
        var dropdowns = [];
        for (let i = 0; i < this.attrs.length; i++) {
            const attr = this.attrs[i];
            dropdowns.push({
                display_name: attr.display_name,
                name: attr.name,
                value: '%',
                options: this._get_options(i, true)
            });
        }

        // put the default values
        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                dropdowns: dropdowns,
                n_papers: data.rs.length
            },
            methods: {
                is_filter_disabled: function(idx) {
                    if (idx == 0) {
                        return false;
                    } else {
                        if (idx == 1 || idx == 2 || idx == 5) {
                            
                            if (this.dropdowns[idx-1].value == '%') {
                                return true;
                            } else {
                                return false;
                            }
                        }

                        // for the Type of combination
                        // this dropdown depends on the value of previous
                        if (idx == 3) {
                            if (this.dropdowns[2].value.toLocaleLowerCase() == 'combination') {
                                return false;
                            } else {
                                return true;
                            }
                        }

                        // for the next, it depends on the m/c value
                        // and also the choose of type of comb
                        if (idx == 4) {
                            if (this.dropdowns[2].value == '%') {
                                return true;
                            } else if ( this.dropdowns[2].value == 'all' ||
                                this.dropdowns[2].value.toLocaleLowerCase() == 'monotherapy') {
                                return false;  
                            } else {
                                // depends on the value of 
                                if (this.dropdowns[3].value == '%') {
                                    return true;
                                } else {
                                    return false;
                                }
                            }
                        }
                    }
                },

                on_filter_value_change: function(event, idx) {
                    var new_val = event.target.value;
                    this.dropdowns[idx].value = new_val;

                    // update the affected
                    if (idx < this.dropdowns.length - 1) {
                        // now, reset all of the following options
                        for (let i = idx + 1; i < this.dropdowns.length; i++) {
                            // reset the value
                            this.dropdowns[i].value = '%';
                            // reset the options
                            this.dropdowns[i].options = vw_studyfilter._get_options(i, true);
                        }
                        
                        if (new_val != '%') {
                            // now, update the options of the next dropdown
                            var next = 1;
                            if (idx == 2 &&
                                new_val.toLocaleLowerCase() == 'all') {
                                next = 2;
                            }
                            if (idx == 2 &&
                                new_val.toLocaleLowerCase() == 'monotherapy') {
                                next = 2;
                            }
                            
                            var next_options = vw_studyfilter._get_options(idx + next);
                            console.log(next_options);
                            this.dropdowns[idx + next].options = next_options;
                        }
                    }

                    // now need to get the pmids
                    // so, first, get the current values of all dropdowns
                    var conditions = [];
                    for (let i = 0; i < this.dropdowns.length; i++) {
                        const dropdown = this.dropdowns[i];
                        var name_i = dropdown.name;
                        var val_i = dropdown.value;
                        if (val_i == '%' || val_i == 'all') {
                            // skip the default
                            // but we still need a condition, so this one
                            conditions.push(
                                '1=1'
                            );
                        } else {
                            conditions.push(
                                '`' + name_i + '` like "%' + val_i + '%"'
                            );
                        }
                    }
                    
                    // second, use the conditions to search for the 
                    var pmids = vw_studyfilter._get_pmids_by_conditions(conditions);
                    this.n_papers = pmids.length;
                    console.log('* filtered studies:', pmids);

                    // send these pmids to the oclist
                    jarvis.update_plots_by_pmids(pmids);

                    // finally, update the filter UI
                    this.$forceUpdate();
                }
            }
        });
    },

    update: function() {
        this.vpp.$data.attrs = attrs;
    },

    _get_pmids_by_conditions: function(conditions) {
        var sql_conds = conditions.join(' and \n');
        var sql = "select PMID from papers " + '\n' +
            "where " + sql_conds + '\n';
        
        var rs = alasql(sql);
        
        var pmids = [];
        for (let i = 0; i < rs.length; i++) {
            const r = rs[i];
            // make sure the PMID is a string
            pmids.push(""+r.PMID);
        }

        return pmids;
    },

    _get_options: function(idx, skip) {
        if (typeof(skip) == 'undefined') {
            // use this option to skip checking, just return the default options
            skip = false;
        }
        var options = [{
            name: '',
            value: '%'
        }, {
            name: 'All',
            value: 'all'
        }];
        var name_idx = this.attrs[idx].name;
        var vals_idx = this.attrs[idx].values;

        if (idx == 0) {
            for (let i = 0; i < this.attrs[idx].values.length; i++) {
                const val = this.attrs[idx].values[i];
                options.push({
                    name: val,
                    value: val
                })
            }
        } else {
            if (skip) {
                return options;
            }
            // for all other dropdown, the option is decided by ALL of the selections
            // of dependencies for example:
            // for the 2nd dropdown, the options are decided by the 1st selection
            // for the 3rd dropdown, the options are decided by the selections of the 1st and 2nd.
            // for the 4th, by 1st, 2nd, and 3rd
            // etc.
            // So, first, need to generate the condition by all previous 
            var conditions = [];
            for (let j = 0; j < idx; j++) {
                var name_j = this.vpp.$data.dropdowns[j].name;
                var val_j = this.vpp.$data.dropdowns[j].value;

                if (val_j == this.blank_val || val_j == 'all') {
                    // skip the blank dropdown
                    // but we still need a condition, so this one
                    conditions.push(
                        '1=1'
                    );
                } else {
                    conditions.push(
                        '`' + name_j + '` like "%' + val_j + '%"'
                    );
                }
            }
            var sql_cond = conditions.join(' and \n');

            // then, use these conditions to query the itable data to get the available records
            var sql = "select `" + name_idx + '` as attr, count(PMID) as cnt ' + '\n' +
                'from papers ' + '\n' +
                'where ' + sql_cond + '\n' +
                'group by `' + name_idx + '` ';

            console.log(sql);
            var rs = alasql(sql);
            console.log(rs);

            // last, check each value whether available in the rs
            for (let i = 0; i < this.attrs[idx].values.length; i++) {
                const val = this.attrs[idx].values[i];
                var val_upper = val.toLocaleUpperCase();

                // check whether this val in rs or not
                for (let j = 0; j < rs.length; j++) {
                    const r = rs[j];

                    if (typeof(r.attr) == 'undefined' ||
                        r.attr == null) {
                        continue;
                    }
                    
                    var R_VAL = r.attr.toLocaleUpperCase();
                    
                    if (R_VAL.lastIndexOf(val_upper)>=0) {
                        // which means this value exists in the selection
                        // Then we could put this val in the result
                        options.push({
                            name: val,
                            value: val
                        });
                        
                        // since we already found this value
                        // just break and check next value
                        break;

                    } else {
                        
                    }
                }
            }
        }

        return options;
    }
};

