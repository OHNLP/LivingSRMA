/**
 * Extractor for Indirectness
 */
Object.assign(pan_ocpapers.vpp_methods, {
    on_change_ind_qs: function() {
        var qs = [
            this.get_working_arm_attrs()['g0']['COE_RCT_IND_Q1_ANSWER'],
            this.get_working_arm_attrs()['g0']['COE_RCT_IND_Q2_ANSWER'],
            this.get_working_arm_attrs()['g0']['COE_RCT_IND_Q3_ANSWER'],
            this.get_working_arm_attrs()['g0']['COE_RCT_IND_Q4_ANSWER'],
            this.get_working_arm_attrs()['g0']['COE_RCT_IND_Q5_ANSWER']
        ];
        var ind_closeness = coe_helper.judge_ind_closeness(qs);
        console.log('* judge_ind_closeness, ',qs,' : ', ind_closeness);
        this.get_working_arm_attrs()['g0']['COE_RCT_IND_OVERALL_AR'] = ind_closeness;
        this.$forceUpdate();
        this.set_has_change_unsaved();
    },

    to_ind_symbol: function(v) {
        if (typeof(v) == 'undefined' || v == '' || v == null) {
            v = 'NA';
        }
        // console.log('* rob symbol:', v);
        var html = '<div class="ind-rst-icon-'+v+'">';
        html += {
            V: '+ Very Close',
            M: '~ Moderately Close',
            N: 'x Not Close',
            NA: '? Not Decided'
        }[v];
        html += '</div>';

        return html;
    }
});