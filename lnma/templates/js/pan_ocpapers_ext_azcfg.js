/**
 * This is a plugin / extension for the pan_ocpapers.
 * 
 * Before using, please import / define the pan_ocpapers
 */

// Extend the vpp data
Object.assign(pan_ocpapers.vpp_data, {
    // the configurations for meta-analysis
    // 
    cfgs: {
        // for pwma, define the treatment arm
        treatment: {
            selected: '',
            is_used: true,
            is_disabled: false,
            options: []
        },

        // for pwma, define the control arm
        control: {
            selected: '',
            is_used: true,
            is_disabled: false,
            options: []
        },

        // for pwma and nma, the value could be in the following list
        // 
        // but in this analyzer, the input_format should come from the oc
        input_format: {
            selected: 'PRIM_CAT_PRE',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Prim | Categorical + Precalculated', value: 'PRIM_CAT_PRE'},
                {text: 'Prim | Categorical + Raw', value: 'PRIM_CAT_RAW'},
                {text: 'Prim | Categorical + Raw (Incidence Rate Ratios)', value: 'PRIM_CATIRR_RAW'},
                {text: 'Prim | Continuous + Precalculated', value: 'PRIM_CONTD_PRE'},
                {text: 'Prim | Continuous + Raw', value: 'PRIM_CONTD_RAW'},

                {text: 'Subg | Categorical + Precalculated', value: 'SUBG_CAT_PRE'},
                {text: 'Subg | Categorical + Raw', value: 'SUBG_CAT_RAW'},
                {text: 'Subg | Categorical + Raw (Incidence Rate Ratios)', value: 'SUBG_CATIRR_RAW'},
                {text: 'Subg | Continuous + Precalculated', value: 'SUBG_CONTD_PRE'},
                {text: 'Subg | Continuous + Raw', value: 'SUBG_CONTD_RAW'},

                {text: 'ADEV | Categorical + Raw for Adverse Event', value: 'PRIM_CAT_RAW_G5'},
            ]
        },

        // for AE analysis only
        ae_grade: {
            selected: 'ga',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'All Grade', value: 'ga'},
                {text: 'Grade 3/4', value: 'g34'},
                {text: 'Grade 3 or Higher', value: 'g3h'},
                {text: 'Grade 5 Only', value: 'g5n'},
            ]
        },

        // for all, model effect
        fixed_or_random: {
            selected: 'random',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Random-Effect', value: 'random'},
                {text: 'Fixed-Effect', value: 'fixed'}
            ]
        },

        pooling_method: {
            selected: 'Inverse',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Inverse Variance', value: 'Inverse'},
                {text: 'Mantel-Haenszel', value: 'MH'},
                {text: 'Peto', value: 'Peto'}
            ]
        },

        pairwise_analysis: {
            selected: 'PRIM',
            use: true,
            disabled: false,
            options: [
                {text: 'Primary Analysis', value: 'PRIM'},
                {text: 'Subgroup Analysis', value: 'SUBG'},
                {text: 'Incidence Analysis', value: 'INCD'},
                {text: 'Adverse Event Analysis', value: 'ADEV'}
            ]
        },

        measure_of_effect: {
            selected: 'OR',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Hazard Ratio', value: 'HR'},
                {text: 'Odds Ratio', value: 'OR'},
                {text: 'Relative Risk', value: 'RR'},
                {text: 'Risk Difference', value: 'RD'},
                {text: 'Incidence Rate Ratio', value: 'IRR'},
                {text: 'Mean Difference', value: 'MD'},
                {text: 'Standardized Mean Difference', value: 'SMD'}
            ]
        },

        tau_estimation_method: {
            selected: 'DL',
            is_used: true,
            is_disabled: false,
            options: [
                { text: 'DerSimonian-Laird', value: 'DL' },
                { text: 'Restricted Maximum-likelihood', value: 'REML' },
                { text: 'Maximum Likelihood', value: 'ML' },
                { text: 'Empirical Bayes', value: 'EB' },
                { text: 'Sidik-Jonkman', value: 'SJ' },
                { text: 'Hedges', value: 'HE' },
                { text: 'Hunter-Schmidt', value: 'HS' },
                { text: 'Paul-Mendel', value: 'PM' }
            ]
        },

        hakn_adjustment: {
            selected: 'no',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'No', value: 'no'},
                {text: 'Yes', value: 'yes'}
            ]
        },

        smd_estimation_method: {
            selected: 'Hedges',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Hedges', value: 'Hedges'},
                {text: "Cohen's d", value: 'Cohen'},
                {text: "Glass delta", value: 'Glass'}
            ]
        },

        prediction_interval: {
            selected: 'no',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Yes', value: 'yes'},
                {text: "No", value: 'no'}
            ]
        },

        sensitivity_analysis: {
            selected: 'no',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Yes', value: 'yes'},
                {text: "No", value: 'no'}
            ]
        },

        sensitivity_analysis_excluded_study_list: {
            selected: []
        },

        cumulative_meta_analysis: {
            selected: 'no',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Yes', value: 'yes'},
                {text: "No", value: 'no'}
            ]
        },

        cumulative_meta_analysis_sortby: {
            selected: 'year',
            options: [
                {text: 'Year', value: 'year'},
                {text: "TE", value: 'TE'}
            ]
        }
    }
});


// Extend the vpp methods
Object.assign(pan_ocpapers.vpp_methods, {
    /**
     * Decide whether to show a config or not
     * 
     * The is_used of some configs are defined by other config(s),
     * so this function helps to decide wheter to display a config or not
     * 
     * By default, the display of a config is decided by the `is_used`
     * @param {string} cfg_name 
     * @returns 
     */
    show_cfg: function(cfg_name) {
        switch (cfg_name) {
            case 'hakn_adjustment':
                if (this.cfgs.fixed_or_random.selected == 'random')
                    this.cfgs.hakn_adjustment.is_used = true;
                else
                    this.cfgs.hakn_adjustment.is_used = false;
                break;
            case 'smd_estimation_method':
                if (this.cfgs.input_format.selected.includes('CONTD_RAW') &&
                    this.cfgs.measure_of_effect.selected == 'SMD')
                    this.cfgs.smd_estimation_method.is_used = true;
                else
                    this.cfgs.smd_estimation_method.is_used = false;
                break;
            case 'sensitivity_analysis':
                if (this.cfgs.pairwise_analysis.selected == 'PRIM')
                    this.cfgs.sensitivity_analysis.is_used = true;
                else
                    this.cfgs.sensitivity_analysis.is_used = false;
                break;
            case 'cumulative_meta_analysis':
                if (this.cfgs.pairwise_analysis.selected == 'PRIM')
                    this.cfgs.cumulative_meta_analysis.is_used = true;
                else
                    this.cfgs.cumulative_meta_analysis.is_used = false;
                break;
            case 'prediction_interval':
                if (this.cfgs.pairwise_analysis.selected == 'PRIM')
                    this.cfgs.prediction_interval.is_used = true;
                else
                    this.cfgs.prediction_interval.is_used = false;
                break;
        }

        return this.cfgs[cfg_name].is_used;
    },

    show_cfg_option: function(cfg_name, option) {
        switch (cfg_name) {
            case 'pooling_method':
                switch (option) {
                    case 'MH':
                        if (this.cfgs.input_format.selected.includes('CAT_RAW') ||
                            this.cfgs.input_format.selected.includes('CATIRR_RAW')) return true;
                        else return false;
                        break;
                    case 'Peto':
                        if (this.cfgs.input_format.selected.includes('CAT_RAW') &&
                            this.cfgs.measure_of_effect.selected == 'OR' &&
                            this.cfgs.fixed_or_random.selected == 'fixed') return true;
                        else return false;
                        break;
                    case 'Inverse':
                        return true;
                }
                break;
            case 'measure_of_effect':
                switch (option) {
                    case 'HR':
                        if (this.cfgs.input_format.selected.includes('CAT_PRE')) return true;
                        else return false;
                        break;
                    case 'OR':
                        if (this.cfgs.input_format.selected.includes('CAT_PRE') ||
                            this.cfgs.input_format.selected.includes('CAT_RAW')) return true;
                        else return false;
                    case 'RR':
                        if (this.cfgs.pooling_method.selected == 'Peto') return false;
                        if (this.cfgs.input_format.selected.includes('CAT_PRE') ||
                            this.cfgs.input_format.selected.includes('CAT_RAW')) return true;
                        else return false;
                    case 'RD':
                        if (this.cfgs.pooling_method.selected == 'Peto') return false;
                        if (this.cfgs.input_format.selected.includes('CAT_PRE') ||
                            this.cfgs.input_format.selected.includes('CAT_RAW')) return true;
                        else return false;
                        break;
                    case 'IRR':
                        if (this.cfgs.input_format.selected.includes('CATIRR_RAW')) return true;
                        else return false;
                        break;
                    case 'MD':
                    case 'SMD':
                        if (this.cfgs.input_format.selected.includes('CONTD_RAW') ||
                            this.cfgs.input_format.selected.includes('CONTD_PRE')) return true;
                        else return false;
                        break;
                }
                break;
            case 'pairwise_analysis':
                switch (option) {
                    case 'PRIM':
                        if (this.cfgs.input_format.selected.includes('PRIM')) return true;
                        else return false;
                    case 'SUBG':
                        if (this.cfgs.input_format.selected.includes('SUBG')) return true;
                        else return false;
                }
                break;
        }
        return true;
    },

    /**
     * Get the records for MA
     * 
     * For most of time, it only depends on the `extract.data`.
     * But for IO project or AE input format, it is different.
     * 
     * We need to get the correct records and apply user selection
     * to make sure the rs could be customized.
     */
    get_rs: function(grade) {
        // try to build this rs
        var rs = [];

        // first of all, we need to support the IO project analysis
        if (this.working_oc.oc_type == 'pwma' &&
            this.working_oc.meta.input_format == 'PRIM_CAT_RAW_G5') {

            if (typeof(grade) == 'undefined') {
                // use the current selected grade
                grade = this.cfgs.ae_grade.selected.toLocaleUpperCase();
            } else {
                grade = grade.toLocaleUpperCase();
            }

            // then depends on which grade is selected
            for (const pid in this.working_oc.data) {
                if (!Object.hasOwnProperty.call(this.working_oc.data, pid)) {
                    continue;   
                }

                // get this paper by a parent method
                var paper = this.get_paper_by_pid(pid);
                if (paper == null) {
                    // which means this study is not included is SR???
                    paper = {
                        authors: pid,
                        year: ''
                    }
                }

                // get some infomation
                // create a record for analyze
                var study = this.get_first_author(paper.authors) + ' ' +
                            this.get_year(paper.pub_date);
                var year = this.get_year(paper.pub_date);

                // get this data
                var d = this.working_oc.data[pid];

                // get data from all arms
                for (let i = 0; i < d.n_arms - 1; i++) {
                    // when i == 0, the main
                    // when i > 0, then other i-1
                    var ext = null;
                    if (i==0) {
                        ext = d.attrs.main;
                    } else {
                        ext = d.attrs.other[i-1];
                        study = study + ' Arm ' + (i + 1);
                    }

                    // now get data
                    var Nt = this.get_int(d.attrs.main.GA_Nt);
                    var Nc = this.get_int(d.attrs.main.GA_Nc);
                    var Et = this.get_int(d.attrs.main[grade + '_Et']);
                    var Ec = this.get_int(d.attrs.main[grade + '_Ec']);

                    // Now need to check the value
                    if (this.isna(Nt) || 
                        this.isna(Nc) || 
                        this.isna(Et) ||
                        this.isna(Ec)) {
                        
                        // console.log('* skip NULL ' + " " + pid + " " + study);
                        continue;
                    }

                    if (Et == 0 && Ec == 0) {
                        console.log('* skip 0t0c ' + " " + pid + " " + study);
                        continue;
                    }
                    var r = {
                        // the must attributes
                        study: study,
                        year: year,
                        Et: Et,
                        Nt: Nt,
                        Ec: Ec,
                        Nc: Nc,

                        // other infomation
                        grade: grade,
                        pid: pid
                    }

                    rs.push(r);
                }
            }
            return rs;
        }
    },

    get_cfg: function() {
        var cfg = srv_analyzer.get_blank_cfg();

        // copy each one
        for (const cfg_name in cfg) {
            if (!Object.hasOwnProperty.call(this.cfgs, cfg_name)) {
                continue;    
            }
            var c = this.cfgs[cfg_name];

            // put the config
            cfg[cfg_name] = c.selected;
        }

        return cfg;
    },

    analyze: function() {
        this.btn_analyze.is_disabled = false;
        jarvis.analyze();
    }
});


// Extend the pan_ocpapers methods
Object.assign(pan_ocpapers, {

});