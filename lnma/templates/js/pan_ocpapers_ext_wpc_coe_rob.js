Object.assign(pan_ocpapers.vpp_methods, {
    /////////////////////////////////////////////////////
    // For the working paper rob extraction
    /////////////////////////////////////////////////////
    show_coe_rob_d: function(d_idx) {
        this.coe_rob_d_active = d_idx;
    },

    load_rob_from_same_trial: function() {
        // get working paper
        let paper = this.working_paper;
        toast('Under development');
    },

    /**
     * Show a question or not based on existing answers
     * @param {Object} ext data extraction
     * @param {int} d_idx index of D
     * @param {int} q_idx index of Question in given D
     */
    show_coe_rob_d_q: function(ext, d_idx, q_idx) {
        
    },

    show_coe_rob_option_NA: function(d_idx, q_idx) {
        if (d_idx != 2) {
            return false;
        }
        if (q_idx == 1 || q_idx == 2 || q_idx == 6 || q_idx == 7) {
            return false;
        }
        // only when 3,4,5 when aim is b
        if (this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_AIM'] == 'b') {
            return true;

        } else {
            return false;
        }
    },

    on_change_rob_q_coment: function() {
        this.set_has_change_unsaved();
    },

    on_change_rob_overall: function() {
        this.set_has_change_unsaved();
    },

    on_change_rob_qs: function() {
        this.update_rob_ds();
        this.update_rob_overall_ar();
        // no matter what happens, trigger this event
        this.set_has_change_unsaved();
    },

    on_change_rob_ds: function() {
        this.update_rob_overall_ar();
        // no matter what happens, trigger this event
        this.set_has_change_unsaved();
    },

    update_rob_overall_ar: function() {
        var ds = ['NA', 'NA', 'NA', "NA", "NA"];
        for (let i = 0; i < ds.length; i++) {
            var d_idx = i+1;
            ds[i] = coe_helper.get_domain(
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D'+d_idx+'_RJ'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D'+d_idx+'_AR']
            );
        }
        var overall = coe_helper.judge_rob_overall(
            ds[0],
            ds[1],
            ds[2],
            ds[3],
            ds[4],
        );

        this.get_working_arm_attrs()['g0']['COE_RCT_ROB_OVERALL_AR'] = overall;
        this.$forceUpdate();
    },

    update_rob_ds: function() {
        for (let i = 1; i <=5 ; i++) {
            this.update_rob_d(i);
        }
        this.$forceUpdate();
    },

    update_rob_d: function(d_idx) {
        if (d_idx == 1) {
            var d1 = coe_helper.judge_rob_d1(
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D1_Q1'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D1_Q2'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D1_Q3']
            );
            this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D1_AR'] = d1;

        } else if (d_idx == 2) {
            var d2 = coe_helper.judge_rob_d2(
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_AIM'],

                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_Q1'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_Q2'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_Q3'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_Q4'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_Q5'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_Q6'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_Q7']
            );
            this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_AR'] = d2;

        } else if (d_idx == 3) {
            var d3 = coe_helper.judge_rob_d3(
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D3_Q1'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D3_Q2'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D3_Q3'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D3_Q4'],
            );
            this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D3_AR'] = d3;

        } else if (d_idx == 4) {
            var d4 = coe_helper.judge_rob_d4(
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D4_Q1'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D4_Q2'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D4_Q3'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D4_Q4'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D4_Q5'],
            );
            this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D4_AR'] = d4;

        } else if (d_idx == 5) {
            var d5 = coe_helper.judge_rob_d5(
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D5_Q1'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D5_Q2'],
                this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D5_Q3'],
            );
            this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D5_AR'] = d5;

        }

    },

    get_qs: function(d_idx) {
        if (d_idx == 2) {
            var aim = this.get_coe_rob_d2_aim();
            if (aim == 'NA') {
                return {};
            } else {
                return this.coe_rob_qs[2][aim];
            }
        } else {
            return this.coe_rob_qs[d_idx]
        }
    },

    disable_rob_domain_question: function(d_idx, q_idx, ext) {
        if (d_idx == 1) {
            return false;

        } else if (d_idx == 2) {
            if (ext['COE_RCT_ROB_D2_AIM'] == 'a') {
                // for aim A
                if (q_idx == 1 || q_idx == 2) {
                    return false;

                } else if (q_idx == 3) {
                    if (ext['COE_RCT_ROB_D2_Q1'] == 'Y'  ||
                        ext['COE_RCT_ROB_D2_Q1'] == 'PY' ||
                        ext['COE_RCT_ROB_D2_Q1'] == 'NI' ||
                        ext['COE_RCT_ROB_D2_Q2'] == 'Y'  ||
                        ext['COE_RCT_ROB_D2_Q2'] == 'PY' ||
                        ext['COE_RCT_ROB_D2_Q2'] == 'NI' ) {
                        return false;

                    } else {
                        return true;
                    }
                } else if (q_idx == 4) {
                    if (ext['COE_RCT_ROB_D2_Q3'] == 'Y'  ||
                        ext['COE_RCT_ROB_D2_Q3'] == 'PY') {
                        return false;

                    } else {
                        return true;
                    }
                } else if (q_idx == 5) {
                    if (ext['COE_RCT_ROB_D2_Q4'] == 'Y'  ||
                        ext['COE_RCT_ROB_D2_Q4'] == 'PY') {
                        return false;

                    } else {
                        return true;
                    }
                } else if (q_idx == 6) {
                    return false;

                } else if (q_idx == 7) {

                    if (ext['COE_RCT_ROB_D2_Q6'] == 'N'  ||
                        ext['COE_RCT_ROB_D2_Q6'] == 'PN'||
                        ext['COE_RCT_ROB_D2_Q6'] == 'NI') {
                        return false;

                    } else {
                        return true;
                    }
                }
            } else {
                // for aim B
                if (q_idx == 1 || q_idx == 2) {
                    return false;

                } else if (q_idx == 3) {
                    if (ext['COE_RCT_ROB_D2_Q1'] == 'Y'  ||
                        ext['COE_RCT_ROB_D2_Q1'] == 'PY' ||
                        ext['COE_RCT_ROB_D2_Q1'] == 'NI' ||
                        ext['COE_RCT_ROB_D2_Q2'] == 'Y'  ||
                        ext['COE_RCT_ROB_D2_Q2'] == 'PY' ||
                        ext['COE_RCT_ROB_D2_Q2'] == 'NI' ) {
                        return false;

                    } else {
                        return true;
                    }
                } else if (q_idx == 4) {
                    return false;

                } else if (q_idx == 5) {
                    return false;
                    
                } else if (q_idx == 6) {
                    
                    if (ext['COE_RCT_ROB_D2_Q3'] == 'N'  ||
                        ext['COE_RCT_ROB_D2_Q3'] == 'PN' ||
                        ext['COE_RCT_ROB_D2_Q3'] == 'NI' ||
                        ext['COE_RCT_ROB_D2_Q4'] == 'Y'  ||
                        ext['COE_RCT_ROB_D2_Q4'] == 'PY' ||
                        ext['COE_RCT_ROB_D2_Q4'] == 'NI' ||
                        ext['COE_RCT_ROB_D2_Q5'] == 'Y'  ||
                        ext['COE_RCT_ROB_D2_Q5'] == 'PY' ||
                        ext['COE_RCT_ROB_D2_Q5'] == 'NI' ) {
                        return false;

                    } else {
                        return true;
                    }
                }
            }
        } else if (d_idx == 3) {
            if (q_idx == 1) {
                return false;

            } else if (q_idx == 2) {
                if (ext['COE_RCT_ROB_D3_Q1'] == 'N'  ||
                    ext['COE_RCT_ROB_D3_Q1'] == 'PN' ||
                    ext['COE_RCT_ROB_D3_Q1'] == 'NI') {
                    return false;
                } else {
                    return true;
                }
            } else if (q_idx == 3) {
                if (ext['COE_RCT_ROB_D3_Q2'] == 'N'  ||
                    ext['COE_RCT_ROB_D3_Q2'] == 'PN' ||
                    ext['COE_RCT_ROB_D3_Q2'] == 'NI') {
                    return false;
                } else {
                    return true;
                }
                
            } else if (q_idx == 4) {
                if (ext['COE_RCT_ROB_D3_Q3'] == 'Y'  ||
                    ext['COE_RCT_ROB_D3_Q3'] == 'PY' ||
                    ext['COE_RCT_ROB_D3_Q3'] == 'NI') {
                    return false;
                } else {
                    return true;
                }
            }

        } else if (d_idx == 4) {
            if (q_idx == 1 || q_idx == 2) {
                return false;

            } else if (q_idx == 3) {
                if (ext['COE_RCT_ROB_D4_Q1'] == 'N'  ||
                    ext['COE_RCT_ROB_D4_Q1'] == 'PN' ||
                    ext['COE_RCT_ROB_D4_Q1'] == 'NI' ||
                    ext['COE_RCT_ROB_D4_Q2'] == 'N'  ||
                    ext['COE_RCT_ROB_D4_Q2'] == 'PN' ||
                    ext['COE_RCT_ROB_D4_Q2'] == 'NI' ) {
                    return false;

                } else {
                    return true;
                }
            } else if (q_idx == 4) {
                if (ext['COE_RCT_ROB_D4_Q3'] == 'Y'  ||
                    ext['COE_RCT_ROB_D4_Q3'] == 'PY' ||
                    ext['COE_RCT_ROB_D4_Q3'] == 'NI') {
                    return false;
                } else {
                    return true;
                }
                
            } else if (q_idx == 5) {
                if (ext['COE_RCT_ROB_D4_Q4'] == 'Y'  ||
                    ext['COE_RCT_ROB_D4_Q4'] == 'PY' ||
                    ext['COE_RCT_ROB_D4_Q4'] == 'NI') {
                    return false;
                } else {
                    return true;
                }
            }
            
        } else if (d_idx == 5) {
            return false;
            
        } else {
            // ????
        }

        return false;
    },

    get_coe_rob_d2_aim: function() {
        var aim = this.get_working_arm_attrs()['g0']['COE_RCT_ROB_D2_AIM'];
        if (aim == null || aim == '') {
            return 'NA';
        }
        return aim;
    },

    to_rob_symbol: function(v) {
        if (typeof(v) == 'undefined' || v == '' || v == null) {
            v = 'NA';
        }
        // console.log('* rob symbol:', v);
        var html = '<div class="rob-rst-icon rob-rst-icon-'+v+'">';
        html += {
            L: '+',
            M: '!',
            H: '-',
            NA: '?'
        }[v];
        html += '</div>';

        return html;
    }
});