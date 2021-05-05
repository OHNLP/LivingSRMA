var srv_analyzer = {
    
    // all urls for analyzer
    url: {
        azoc: "[[ url_for('analyzer.azoc') ]]",
        analyze: "[[ url_for('analyzer.analyze') ]]",

        get_paper: "[[ url_for('analyzer.get_paper') ]]",
        get_extract: "[[ url_for('analyzer.get_extract') ]]",
        get_extracts: "[[ url_for('analyzer.get_extracts') ]]",
        get_extract_and_papers: "[[ url_for('analyzer.get_extract_and_papers') ]]",
    },

    // the project information
    projct: null,

    // the configs for analyzer
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
            selected: 'FALSE',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Yes', value: 'TRUE'},
                {text: 'No', value: 'FALSE'}
            ]
        },

        adhoc_hakn: {
            selected: '',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Not Applied', value: ''},
                {text: 'SE', value: 'se'},
                {text: 'CI', value: 'ci'}
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
            selected: 'FALSE',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Yes', value: 'TRUE'},
                {text: "No", value: 'FALSE'}
            ]
        },

        incidence_analysis: {
            selected: 'no',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'Yes', value: 'yes'},
                {text: "No", value: 'no'}
            ]
        },

        incd_sm: {
            selected: 'PLOGIT',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'PLOGIT', value: 'PLOGIT'},
                {text: "PLN", value: 'PLN'},
                {text: 'PRAW', value: 'PRAW'},
                {text: 'PAS', value: 'PAS'},
                {text: 'PFT', value: 'PFT'}
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
            selected: 'yes',
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
        },

        // for cumulative analysis
        assumed_baseline: {
            selected: 100,
            is_used: true,
            is_disabled: false,
            options: [
                {text: '100', value: 100},
                {text: '1000', value: 1000},
            ]
        },

        // generate plots by raw script?
        is_create_figure: {
            selected: 'NO',
            is_used: true,
            is_disabled: false,
            options: [
                {text: 'No', value: 'no'},
                {text: 'Yes', value: 'yes'},
            ]
        }
    },

    /**
     * Decide whether to display a config or not
     * Some config depends other config's selection
     * 
     * @param {string} cfg_name The variable name of the configuration
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
            case 'adhoc_hakn':
                if (this.cfgs.fixed_or_random.selected == 'random' && 
                    this.cfgs.hakn_adjustment.selected == 'yes')
                    this.cfgs.hakn_adjustment.is_used = true;
                else
                    this.cfgs.hakn_adjustment.is_used = false;
                break;
            case 'incidence_analysis':
                if (this.cfgs.input_format.selected.includes('CAT_RAW'))
                    this.cfgs.incidence_analysis.is_used = true;
                else
                    this.cfgs.incidence_analysis.is_used = false;
                break;
        }

        return this.cfgs[cfg_name].is_used;
    },

    /**
     * Decided whether to show an option in a config.
     * 
     * @param {string} cfg_name The variable name of the config
     * @param {string} option One option value of the config
     * @returns 
     */
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

    // helper functions
    get_blank_cfg: function() {
        // return {
        //     _analyze_type: null,
        //     input_format: null,
        //     measure_of_effect: null,
        //     fixed_or_random: null,
        //     which_is_better: null,

        //     // for nma
        //     analysis_method: null,
        //     reference_treatment: null,

        //     // for pwma and subg
        //     pairwise_analysis: null,
        //     pooling_method: null,
        //     tau_estimation_method: null,
        //     hakn_adjustment: null,
        //     smd_estimation_method: null,
        //     prediction_interval: null,
        //     sensitivity_analysis: null,
        //     cumulative_meta_analysis: null,
        //     cumulative_meta_analysis_sortby: null,
        //     treatment: null,
        //     control: null
        // };
        var cfg = {};
        
        for (const key in this.cfgs) {
            if (Object.hasOwnProperty.call(this.cfgs, key)) {
                const item = this.cfgs[key];
                cfg[key] = item.selected;
            }
        }

        return cfg;
    },

    analyze_pwma_aegs: function() {

    },

    analyze_pwma_prim: function(
        rs,
        input_format,
        measure_of_effect,
        fixed_or_random,
        which_is_better,

        pooling_method,
        tau_estimation_method,
        hakn_adjustment,
        smd_estimation_method,
        prediction_interval,
        sensitivity_analysis,
        cumulative_meta_analysis,
        cumulative_meta_analysis_sortby,
    ) {
        // the analyze type for backend
        var _analyze_type = 'pwma';
        var pairwise_analysis = 'PRIM';

        // set default settings
        if (typeof(pooling_method) == 'undefined') {
            pooling_method = 'Inverse';
        }
        if (typeof(tau_estimation_method) == 'undefined') {
            tau_estimation_method = 'DL';
        }
        if (typeof(hakn_adjustment) == 'undefined') {
            hakn_adjustment = 'no';
        }
        if (typeof(smd_estimation_method) == 'undefined') {
            smd_estimation_method = 'Hedges';
        }
        if (typeof(prediction_interval) == 'undefined') {
            prediction_interval = false;
        }
        if (typeof(sensitivity_analysis) == 'undefined') {
            sensitivity_analysis = false;
        }
        if (typeof(cumulative_meta_analysis) == 'undefined') {
            cumulative_meta_analysis = false;
        }
        if (typeof(cumulative_meta_analysis_sortby) == 'undefined') {
            cumulative_meta_analysis_sortby = 'year';
        }

        // TODO get the other 

        // build the cfg for submission
        var cfg = {
            _analyze_type: _analyze_type,
            input_format: input_format,
            measure_of_effect: measure_of_effect,
            fixed_or_random: fixed_or_random,
            which_is_better: which_is_better,

            pairwise_analysis: pairwise_analysis,
            pooling_method: pooling_method,
            tau_estimation_method: tau_estimation_method,
            hakn_adjustment: hakn_adjustment,
            smd_estimation_method: smd_estimation_method,
            prediction_interval: prediction_interval,
            sensitivity_analysis: sensitivity_analysis,
            cumulative_meta_analysis: cumulative_meta_analysis,
            cumulative_meta_analysis_sortby: cumulative_meta_analysis_sortby
        };

        // call the analyzer service

        this.analyze(cfg, rs, function(data) {
            console.log(data);
        });
    },

    analyze_pwma_subg: function(
        rs,
        input_format,
        measure_of_effect,
        fixed_or_random,
        which_is_better,
        
        pooling_method,
        tau_estimation_method,
        hakn_adjustment,
    ) {
        // the analyze type for backend
        var _analyze_type = 'pwma';
        var pairwise_analysis = 'SUBG';

        // set default settings
        if (typeof(pooling_method) == 'undefined') {
            pooling_method = 'Inverse';
        }
        if (typeof(tau_estimation_method) == 'undefined') {
            tau_estimation_method = 'DL';
        }
        if (typeof(hakn_adjustment) == 'undefined') {
            hakn_adjustment = 'no';
        }

        var prediction_interval = false;
        var sensitivity_analysis = false;
        var cumulative_meta_analysis = false;

        // TODO get the other 

        // build the cfg for submission
        var cfg = {
            _analyze_type: _analyze_type,
            input_format: input_format,
            pairwise_analysis: pairwise_analysis,
            measure_of_effect: measure_of_effect,
            fixed_or_random: fixed_or_random,
            pooling_method: pooling_method,
            tau_estimation_method: tau_estimation_method,
            hakn_adjustment: hakn_adjustment,
            prediction_interval: prediction_interval,
            sensitivity_analysis: sensitivity_analysis,
            cumulative_meta_analysis: cumulative_meta_analysis
        };

        // call the analyzer service

        this.analyze(cfg, rs, function(data) {
            console.log(data);
        });
    },

    analyze_nma: function() {
        
    },

    /**
     * Interface function for submitting analyze request
     * @param {Object} cfg the configuration of the analysis
     * @param {List} rs the results
     * @param {function} callback the callback function for ajax
     */
    analyze: function(cfg, rs, callback) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: this.url.analyze,
            data: {
                rs: JSON.stringify(rs), 
                cfg: JSON.stringify(cfg) 
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when analyzing', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    /**
     * Get a paper
     * @param {string} pid 
     * @param {function} callback the callback for ajax
     */
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
};