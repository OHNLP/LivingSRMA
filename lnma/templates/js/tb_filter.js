var tb_filter = {
    vpp: null,
    vpp_id: '#tb_filter',
    /**
     * Filters
     * To manage the filters for selecting records
     * I add this module to organize the filters.
     * Each filter is defined as follows:
       filter = {
           display_name: 'Just a title for this filter',
           type: 'radio', // or 'checkbox', we will add this later
           attr: 'the attr name for this option', // this MUST be same to attrs
           oper: '=', // =, >, <, >=, <=, in, <>, operators in SQL
           values: [{
               display_name: 'Just a option for this option',
               value: 'xxx',
               default: true, // use this value as default for this filter
               sql_cond: 'xx != NULL' // this is optional, if sql_cond exist, ignore value
           }, { ... }]
       }
     */
    all_filters: {
        CAT: [
        /**
         * Filters for CAT
         */
        {
            display_name: 'Treatment arm',
            type: 'radio',
            attr: "TARM",
            value: 0,
            values: [
                { display_name: 'All treatments', value: 0, sql_cond: '{$col} is not NULL', default: true },
                { display_name: 'Only DOAC', value: 1, sql_cond: "{$col} like '%DOAC%'" },
                { display_name: 'Only LMWH', value: 2, sql_cond: "{$col} like '%LMWH%'" }
            ]
        },
        {
            display_name: 'Control arm',
            type: 'radio',
            attr: "Control arm",
            value: 0,
            values: [
                { display_name: 'All treatments', value: 0, sql_cond: '{$col} is not NULL', default: true },
                { display_name: 'Only LMWH', value: 1, sql_cond: "upper({$col}) like '%LMWH%'" },
                { display_name: 'Only VKA', value: 2, sql_cond: "upper({$col}) like '%VKA%'" }
            ]
        },
        {
            display_name: 'On-treatment duration (months)',
            type: 'radio',
            attr: "On-treatment duration (months)",
            value: 0,
            values: [
                { display_name: 'All', value: 0, sql_cond: '{$col} is not NULL', default: true },
                { display_name: 'Only up to 3', value: 1, sql_cond: "{$col} like '%up to 3%'" },
                { display_name: 'Only up to 6', value: 2, sql_cond: "{$col} like '%up to 6%'" },
                { display_name: 'Only up to 12', value: 3, sql_cond: "{$col} like '%up to 12%'" }
            ]
        },
        {
            display_name: 'Status of cancer included during randomization',
            type: 'radio',
            attr: "Status of cancer included during randomization",
            value: 0,
            values: [
                { display_name: 'All', value: 0, sql_cond: '{$col} is not NULL', default: true },
                { display_name: 'Active cancer + Hx of cancer', value: 1, sql_cond: "{$col} like '%Hx%'" },
                { display_name: 'Active cancer only', value: 2, sql_cond: "{$col} like '%only%'" },
                { display_name: 'Not-specified', value: 3, sql_cond: "{$col} like '%specified%'" }
            ]
        },
        {
            display_name: 'Primary brain cancer patients',
            type: 'radio',
            attr: "Primary brain cancer patients",
            value: 0,
            values: [
                { display_name: 'All', value: 0, sql_cond: '{$col} is not NULL', default: true },
                { display_name: 'Included', value: 1, sql_cond: "{$col} = 'Included'" },
                { display_name: 'Not Included', value: 2, sql_cond: "{$col} = 'Not Included'" },
                { display_name: 'Not-specified', value: 3, sql_cond: "{$col} like '%specified%'" }
            ]
        },
        {
            display_name: 'Unusual VTE location',
            type: 'radio',
            attr: "Unusual VTE location",
            value: 0,
            values: [
                { display_name: 'All', value: 0, sql_cond: '{$col} is not NULL', default: true },
                { display_name: 'Included', value: 1, sql_cond: "{$col} = 'Included'" },
                { display_name: 'Not Included', value: 2, sql_cond: "{$col} = 'Not Included'" }
            ]
        },
        {
            display_name: 'Included in Meta-Analysis?',
            type: 'radio',
            attr: "Included in Meta-Analysis",
            value: 0,
            values: [
                { display_name: 'All', value: 0, sql_cond: '{$col} is not NULL', default: true },
                { display_name: 'YES', value: 1, sql_cond: "{$col} like '%YES%'" },
                { display_name: 'NO', value: 2, sql_cond: "{$col} like '%NO%'" }
            ]
        }
        ]
    },
    filters: [
    /**
     * Filters for RCC
     */
    {
        display_name: 'Is Trial included in meta-analysis?',
        type: 'radio',
        attr: 'Is study included in Meta-analysis',
        value: 0,
        values: [
            { display_name: 'All Studies', value: 0, sql_cond: "{$col} is not NULL"},
            { display_name: 'Meta-Analysis Only', value: 1, sql_cond: "{$col} like '%yes%'"},
            { display_name: 'Systematic Review Only', value: 2, sql_cond: "{$col} like '%no%'"}
        ]
    }, {
        display_name: 'Number of Arms',
        type: 'radio',
        attr: "Number of Arms",
        value: 0,
        values: [
            { display_name: 'Both Two and Three Arms', value: 0, sql_cond: "{$col} is not NULL", default: true },
            { display_name: 'Two Arms', value: 1, sql_cond: "{$col} in (2)" },
            { display_name: 'Three Arms', value: 2, sql_cond: "{$col} in (3)" }
        ]
    }, {
        display_name: 'Phase of clinical trial?',
        type: 'radio',
        attr: "Phase",
        value: 0,
        values: [
            { display_name: 'All Phases', value: 0, sql_cond: "{$col} is not NULL", default: true },
            { display_name: 'Phase 2', value: 1, sql_cond: "{$col} in (2)" },
            { display_name: 'Phase 3', value: 2, sql_cond: "{$col} in (3)" }
        ]
    }, {
        display_name: 'What’s in the treatment arm?',
        type: 'radio',
        attr: "Type of Agent in Treatment Arm",
        value: 0,
        values: [
            { display_name: 'All Types', value: 0, sql_cond: "{$col} is not NULL" },
            { display_name: 'IO + IO', value: 1, sql_cond: "({$col} like '%IO%' and upper({$col}) not like '%TKI%')" },
            { display_name: 'Only TKI', value: 2, sql_cond: "({$col} like '%TKI%' and upper({$col}) not like '%IO%')" },
            { display_name: 'IO + TKI Combination', value: 3, sql_cond: "{$col} like '%IO%' and {$col} like '%TKI%'", default: true }
        ]
    }, {
        display_name: 'Risk categories',
        type: 'radio',
        attr: "Risk Category Included in Trial",
        value: 0,
        values: [
            { display_name: 'All Risk Categories', value: 0, sql_cond: '{$col} is not NULL', default: true },
            { display_name: 'Only Poor and Intermediate Risk', value: 1, sql_cond: "(upper({$col}) like '%POOR%' and upper({$col}) like '%INTERMEDIATE%' and upper({$col}) not like '%FAVORABLE%')" }
        ]
    }, {
        display_name: 'Data Availability',
        type: 'radio',
        attr: "Is OS data available",
        value: 0,
        values: [
            { display_name: 'All', value: 0, sql_cond: '{$col} is not NULL', default: true },
            { display_name: 'OS Data Available', value: 1, sql_cond: "upper({$col}) like '%YES%'" },
            { display_name: 'OS Data NOT Available', value: 2, sql_cond: "upper({$col}) like '%NO%'" }
        ]
    }, {
        display_name: 'Studies with longer followup',
        type: 'radio',
        attr: "Original/Follow Up",
        value: 0,
        values: [
            { display_name: 'All versions', value: 0, sql_cond: '{$col} is not NULL', default: true },
            { display_name: 'Only original', value: 1, sql_cond: "upper({$col}) like '%ORIGINAL%'" },
            { display_name: 'Only followup', value: 2, sql_cond: "upper({$col}) like '%FOLLOW%'" }
        ]
    }
    
    ],


    init: function() {
        // select acceptable filters
        // to use this feature, must init the dt_tbcore at begin!
        var fs = [];
        for (let i = 0; i < this.filters.length; i++) {
            const f = this.filters[i];
            if (dt_tbcore.has_attr(f.attr)) {
                // add the attr_id
                f.attr_id = dt_tbcore.get_attr(f.attr).attr_id;
                fs.push(f);
            }
        }

        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                filters: fs
            },
            methods: {
                reset: function(evt) {
                    for (let i = 0; i < this.filters.length; i++) {
                        const filter = this.filters[i];
                        filter.value = 0;
                    }
                    jarvis.update_schtab();
                },

                update_table: function(evt) {
                    jarvis.update_schtab();
                }
            }
        });
    },

    get_all_sql_conds: function() {
        var sql_conds = [];
        for (let i = 0; i < this.vpp.filters.length; i++) {
            const filter = this.vpp.filters[i];
            var col = dt_tbcore.t_a2c[filter.attr_id];
            var cond = filter.values[filter.value].sql_cond;

            // replace the {$col} with real col name, such as col32, col24
            cond = cond.replace(/\{\$col\}/g, col);

            // add this cond
            sql_conds.push(cond);
        }
        return sql_conds.join('\n  and ');
    }
};