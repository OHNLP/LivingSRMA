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
                {text: 'Subgroup Analysis', value: 'SUBG'}
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

    analyze: function() {
        this.btn_analyze.is_disabled = false;
        jarvis.analyze();
    }
});


// Extend the pan_ocpapers methods
Object.assign(pan_ocpapers, {
});