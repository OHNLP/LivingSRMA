/**
 * The LISR analyzer object for NMA and PWMA analysis
 */
var lisr_analyzer = {

    url: {
        analyze: "[[ url_for('analyzer.analyze') ]]"
    },

    get_blank_cfg: function() {
        return {
            _analyze_type: null,
            input_format: null,
            measure_of_effect: null,
            fixed_or_random: null,
            which_is_better: null,

            // for nma
            analysis_method: null,
            reference_treatment: null,

            // for pwma and subg
            pairwise_analysis: null,
            pooling_method: null,
            tau_estimation_method: null,
            hakn_adjustment: null,
            smd_estimation_method: null,
            prediction_interval: null,
            sensitivity_analysis: null,
            cumulative_meta_analysis: null,
            cumulative_meta_analysis_sortby: null,
            treatment: null,
            control: null
        };
    },

    pwma_primary: function(
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

    pwma_subgroup: function(
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

    nma: function() {
        
    },

    /**
     * Interface function for submitting analyze request
     * @param {Object} cfg the configuration of the analysis
     * @param {List} rs the results
     * @param {function} callback the callback function for ajax
     */
    analyze: function(cfg, rs, callback) {
        $.post(
            this.url.analyze,
            {rs: JSON.stringify(rs), cfg: JSON.stringify(cfg) },
            callback,
            'json'
        );
    }
};