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

    // 8/3/2020: the filters are moved to seperate files for each project
    filters: [],


    init: function() {
        // select acceptable filters
        // to use this feature, must init the dt_tbcore at begin!
        var fs = [];
        for (var i = 0; i < this.filters.length; i++) {
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
        for (var i = 0; i < this.vpp.filters.length; i++) {
            var filter = this.vpp.filters[i];
            var col = dt_tbcore.t_a2c[filter.attr_id];
            var cond = filter.values[filter.value].sql_cond;

            // replace the {$col} with real col name, such as col32, col24
            cond = cond.replace(/\{\$col\}/g, col);

            // add this cond
            sql_conds.push(cond);
        }
        if (sql_conds.length == 0) {
            return '1=1';
        } else {
            return sql_conds.join('\n  and ');
        }
    }
};