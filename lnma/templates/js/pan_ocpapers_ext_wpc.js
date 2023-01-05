/**
 * This is a plugin / extension for the pan_ocpapers.
 * 
 * Before using this one, include or define pan_ocpapers
 */

// Extend the vpp data
Object.assign(pan_ocpapers.vpp_data, {

    // the whether showing the working paper collector
    show_working_paper_collector: false,

    // for the copy function
    // this is a object for the itable
    working_itable: null,

    // the working oc
    working_oc: null,

    // the working paper
    working_paper: null,

    // working arm
    // null means main arm
    // numbers mean other arm
    working_paper_arm: null,

    // working group idx
    // by default, this is 0 for all extract except subg analysis
    working_paper_subg: 0,


    // working autocomplete flag
    // we need to update this flag only when:
    // 1. switch to a different oc/itable
    // 2. switch to a different arm
    is_wp_ac_inited: true,

    // is saving something?
    is_saving: false,

    // detect changes
    has_saved: true,

    // working paper filter for the outcome name
    working_paper_oc_fileter: '',

    // for coe's rob
    coe_rob_d_active: 1,
    coe_rob_d_name: {
        1: 'Domain 1: Risk of bias arising from the randomization process',
        2: "Domain 2: Risk of bias due to deviations from the intended interventions",
        3: "Domain 3: Risk of bias due to missing outcome data",
        4: "Domain 4: Risk of bias in measurement of the outcome",
        5: "Domain 5: Risk of bias in selection of the reported result",
    },
    coe_rob_qs: {
        1: {
            1: "1.1 Was the allocation sequence random?",
            2: "1.2 Was the allocation sequence concealed until participants were enrolled and assigned to interventions?",
            3: "1.3 Did baseline differences between intervention groups suggest a problem with the randomization process?"
        },
        2: {
            a: {
                1: "2.1 Were participants aware of their assigned intervention during the trial?",
                2: "2.2 Were carers and people delivering the interventions aware of participants' assigned intervention during the trial?",
                3: "2.3 If Y/PY/NI to 2.1 or 2.2: Were there deviations from the intended intervention that arose because of the trial context?",
                4: "2.4 If Y/PY to 2.3: Were these deviations likely to have affected the outcome?",
                5: "2.5. If Y/PY/NI to 2.4: Were these deviations from intended intervention balanced between groups?",
                6: "2.6 Was an appropriate analysis used to estimate the effect of assignment to intervention?",
                7: "2.7 If N/PN/NI to 2.6: Was there potential for a substantial impact (on the result) of the failure to analyse participants in the group to which they were randomized?"
            },
            b: {
                1: "2.1 Were participants aware of their assigned intervention during the trial?",
                2: "2.2 Were carers and people delivering the interventions aware of participants' assigned intervention during the trial?",
                3: "2.3 [If applicable:] If Y/PY/NI to 2.1 or 2.2: Were important nonprotocol interventions balanced across intervention groups?",
                4: "2.4 [If applicable:] Were there failures in implementing the intervention that could have affected the outcome?",
                5: "2.5 [If applicable:] Was there non-adherence to the assigned intervention regimen that could have affected participants' outcomes?",
                6: "2.6 If N/PN/NI to 2.3, or Y/PY/NI to 2.4 or 2.5: Was an appropriate analysis used to estimate the effect of adhering to the intervention?"
            }
        },
        3: {
            1: "3.1 Were data for this outcome available for all, or nearly all, participants randomized?",
            2: "3.2 If N/PN/NI to 3.1: Is there evidence that the result was not biased by missing outcome data?",
            3: "3.3 If N/PN to 3.2: Could missingness in the outcome depend on its true value?",
            4: "3.4 If Y/PY/NI to 3.3: Is it likely that missingness in the outcome depended on its true value?"
        },
        4: {
            1: "4.1 Was the method of measuring the outcome inappropriate?",
            2: "4.2 Could measurement or ascertainment of the outcome have differed between intervention groups?",
            3: "4.3 If N/PN/NI to 4.1 and 4.2: Were outcome assessors aware of the intervention received by study participants?",
            4: "4.4 If Y/PY/NI to 4.3: Could assessment of the outcome have been influenced by knowledge of intervention received?",
            5: "4.5 If Y/PY/NI to 4.4: Is it likely that assessment of the outcome was influenced by knowledge of intervention received?"
        },
        5: {
            1: "5.1 Were the data that produced this result analysed in accordance with a pre-specified analysis plan that was finalized before unblinded outcome data were available for analysis?",
            2: "5.2 ... multiple eligible outcome measurements (e.g. scales, definitions, time points) within the outcome domain?",
            3: "5.3 ... multiple eligible analyses of the data?"
        }
    },

    // for Indirectness
    coe_ind_qs: {
        1: '1. The population is similar',
        2: '2. The intervention is similar',
        3: '3. The control is similar',
        4: '4. The outcome is similar',
        5: '5. The method, timeline is similar',
    }
});

// Extend the vpp methods
Object.assign(pan_ocpapers.vpp_methods, {
    /////////////////////////////////////////////////////
    // For the working paper rob extraction
    /////////////////////////////////////////////////////
    show_coe_rob_d: function(d_idx) {
        this.coe_rob_d_active = d_idx;
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
        this.has_change_unsaved();
    },

    on_change_rob_overall: function() {
        this.has_change_unsaved();
    },

    on_change_rob_qs: function() {
        this.update_rob_ds();
        this.update_rob_overall_ar();
        // no matter what happens, trigger this event
        this.has_change_unsaved();
    },

    on_change_rob_ds: function() {
        this.update_rob_overall_ar();
        // no matter what happens, trigger this event
        this.has_change_unsaved();
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
    },

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
        this.has_change_unsaved();
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
    },

    /////////////////////////////////////////////////////
    // For the working paper extraction
    /////////////////////////////////////////////////////
    is_show_attr: function(abbr) {
        if (this.hasOwnProperty('show_attrs')) {
            if (this.show_attrs.hasOwnProperty(abbr)) {
                return this.show_attrs[abbr];
            } else {
                return true;
            }
        } else {
            return true;
        }
    },

    saving_start: function() {
        this.is_saving = true;
    },

    saving_end: function() {
        this.is_saving = false;
        this.has_saved = true;
    },

    has_change_unsaved: function() {
        this.has_saved = false;
    },

    has_change_saved: function() {
        this.has_saved = true;
    },

    confirm_close_wpc: function() {

    },

    on_change_input_value: function(event) {
        // no matter what happens, trigger this event
        this.has_change_unsaved();
    },

    save_working_paper_extraction: function() {
        var pid = this.working_paper.pid;
        var oc = this.working_oc;

        this.saving_start();

        pan_ocpapers.save_working_paper_extraction(
            pid, oc
        );
    },

    fill_working_paper_attrs: function() {
        var project_id = Cookies.get('project_id');
        var cq_abbr = Cookies.get('cq_abbr');
        var pid = this.working_paper.pid;

        // first, try to get the latest itable
        srv_extractor.get_pdata_in_itable(
            project_id,
            cq_abbr,
            pid,
            function(data) {
                console.log('* got itable pdata:', data)
                // then, with the itable, try to fill?
                if (data.success) {
                    pan_ocpapers.fill_working_paper_attrs(
                        data.extract
                    );
                } else {
                    jarvis.toast('Data are not available for this paper in the Interactive Table', 'warning');
                }
            }
        );
    },

    set_n_arms: function() {
        // notify unsaved changes first
        this.has_change_unsaved();

        var n_arms = parseInt(
            this.working_oc.data[this.working_paper.pid].n_arms
        );
        console.log('* set n_arms to', n_arms);

        // update the other to match the number
        this.working_oc.data[this.working_paper.pid] = srv_extractor.set_n_arms(
            this.working_oc.data[this.working_paper.pid], n_arms
        );

        // update current working arm to main
        this.switch_working_arm(null);
        
        this.$forceUpdate();
    },

    switch_working_arm: function(arm_idx) {
        console.log('* switch_working_arm', arm_idx);
        this.working_paper_arm = arm_idx;

        // update the working arm
        $('.w-arm-tab').removeClass('btn-primary');
        $('#working_paper_arm_tab_' + arm_idx).addClass('btn-primary');
    },

    switch_working_subg: function(subg_idx) {
        if (this.working_oc.meta)
        // console.log('* switch subg to ' + subg_idx);
        this.working_paper_subg = subg_idx;
    },

    get_working_arm_attrs: function() {
        // console.log('* get_working_arm_attrs: ' + this.working_paper_arm);
        if (this.working_paper_arm == null) {
            return this.working_oc.data[this.working_paper.pid].attrs.main;
        } else {
            return this.working_oc.data[this.working_paper.pid].attrs.other[this.working_paper_arm];
        }
    },

    set_working_paper_arm_by_group_attr_value: function(g_idx, abbr, value) {
        var old_val = this.get_working_arm_attrs()['g'+g_idx][abbr];
        this.get_working_arm_attrs()['g'+g_idx][abbr] = value;
        console.log('* set value ' + old_val + ' -> ' + this.get_working_arm_attrs()['g'+g_idx][abbr]);
        
        // notify changed
        this.has_change_unsaved();

        this.$forceUpdate();
    },

    set_working_paper_arm_group_by_attr_value: function(abbr, value) {
        var old_val = this.get_working_arm_attrs()['g'+this.working_paper_subg][abbr];
        this.get_working_arm_attrs()['g'+this.working_paper_subg][abbr] = value;
        console.log('* set wk_pp_arm_group value ' + old_val + ' -> ' + value);
        // notify changed
        this.has_change_unsaved();
    },

    set_working_paper_arm_allgroups_by_attr_value: function(abbr, value) {
        for (let i = 0; i < this.working_oc.meta.sub_groups.length; i++) {        
            this.get_working_arm_attrs()['g'+i][abbr] = value;
        }
        // notify changed
        this.has_change_unsaved();
    },


    clear_working_arm_attr: function(g_idx, abbr) {
        this.get_working_arm_attrs()['g'+g_idx][abbr] = '';
        this.has_change_unsaved();
    },

    /**
     * Get the extracted data by the given info
     * 
     * which sub group?
     * which attr or attr_sub?
     */
     get_working_arm_extracted_value: function(group_idx, attr_sub_abbr) {
        if (!this.working_oc.data.hasOwnProperty(this.working_paper.pid)) {
            // no such paper???
            return '';
        }
        if (this.working_paper_arm == null) {
            // check the main arm
            if (!this.working_oc.data[this.working_paper.pid].attrs.main.hasOwnProperty('g' + group_idx)) {
                // no such group in the main arm?
                return '';

            } else {
                if (!this.working_oc.data[this.working_paper.pid].attrs.main['g'+group_idx].hasOwnProperty(attr_sub_abbr)) {
                    // no such attr in this main arm?
                    return ''
                } else {
                    return this.working_oc.data[this.working_paper.pid].attrs.main['g'+group_idx][attr_sub_abbr];
                }
            }
        } else {
            // check the other arm
            if (!this.working_oc.data[this.working_paper.pid].attrs.other[this.working_paper_arm].hasOwnProperty('g' + group_idx)) {
                // no such group in the other arm?
                return '';

            } else {
                if (!this.working_oc.data[this.working_paper.pid].attrs.other[this.working_paper_arm]['g'+group_idx].hasOwnProperty(attr_sub_abbr)) {
                    // no such attr in this other arm?
                    return ''
                } else {
                    return this.working_oc.data[this.working_paper.pid].attrs.other[this.working_paper_arm]['g'+group_idx][attr_sub_abbr];
                }
            }
        }

    },

    is_substr: function(text, sub) {
        if (typeof(sub)=='undefined' || sub == null) {
            return true;
        }
        sub = sub.trim();
        var upper_text = text.toLocaleUpperCase();
        var upper_sub = sub.toLocaleUpperCase();
        if (upper_text.indexOf(upper_sub) >= 0) {
            return true;
        } else {
            return false;
        }
    },

    clear_input: function() {

    }
});

// Extend the pan_ocpapers methods
Object.assign(pan_ocpapers, {
    
    ///////////////////////////////////////////////////////////////////////////
    // Functions related to collector
    ///////////////////////////////////////////////////////////////////////////

    fill_working_paper_attrs: function(itable) {
        // get working pid
        var pid = this.vpp.working_paper.pid;
        console.log('* found working paper pid:', pid);

        // so, there are some pairs
        var afs = JSON.parse(JSON.stringify(
            srv_extractor.project.settings.auto_fill
        ));
        console.log('* get auto fill:', afs);

        // build a dictionary for finding the abbr
        var dict_itable = srv_extractor.mk_oc_name2abbr_dict(itable);
        var dict_oc = srv_extractor.mk_oc_name2abbr_dict(this.vpp.working_oc);

        console.log('* created itable dict:', dict_itable);
        console.log('* created working oc dict:', dict_oc);

        // first, find the abbr for each attr_from
        for (let i = 0; i < afs.length; i++) {            
            afs[i].from_abbr = dict_itable[
                afs[i].from.toLocaleUpperCase()
            ];
            afs[i].to_abbr = dict_oc[
                afs[i].to.toLocaleUpperCase()
            ];

            // second, for each fill, get the values
            // 2021-07-12: add default sub group g0 to itable
            afs[i].from_value = itable.data[pid].attrs.main['g0'][afs[i].from_abbr];

            // now, put this value to the paper of this working oc
            this.vpp.set_working_paper_arm_allgroups_by_attr_value(
                afs[i].to_abbr,
                afs[i].from_value
            );
        }
        console.log('* get abbr for auto fill:', afs);

        // last, update the ui
        this.vpp.$forceUpdate();

        // show some information
        jarvis.toast('Filled the data successfully.')
    },

    /**
     * Update the auto-complete
     */
    update_autocomplete: function() {
        console.time('* update autocomplete');
        $('.input-auto-complete').each(function(idx, elem) {
            var has_ac = $(elem).hasClass('ui-autocomplete-input');

            var abbr = $(elem).attr('abbr');
            var g_idx = $(elem).attr('g_idx');
            
            // get the values
            var values = pan_ocpapers._get_values_by_abbr(abbr, g_idx);

            if (values.length == 0) {
                // no value for this abbr yet
                // so, just stop update
                return;
            }

            $(elem).autocomplete({
                source: values,
                minLength: 0,

                select: function (e, ui) {
                    // console.log("selected!", e, ui);
                    var abbr = $(e.target).attr('abbr');
                    var g_idx = $(e.target).attr('g_idx');
                    var pid = pan_ocpapers.vpp.$data.working_paper.pid;
                    var val = ui.item.value;

                    // set the value
                    // pan_ocpapers.vpp.$data.working_oc.data[pid].attrs.main[abbr] = val;
                    console.log('* selected [', val, '] for g', g_idx, 'abbr', abbr, 'of', pid);

                    // notify the changes
                    pan_ocpapers.vpp.has_change_unsaved();

                    // 2021-04-24: finally fixed this issue!!!
                    // the working arm may be main or other,
                    // need to use the get_working_arm_attrs() to get the current arm
                    // set the value to the working arm
                    pan_ocpapers.vpp.get_working_arm_attrs()['g'+g_idx][abbr] = val;
                },

                change: function (e, ui) {
                    // console.log("changed!", e, ui);
                }

            });
            // console.log('* updated ac for ' + abbr + ' with values', values);

            // 2021-08-31: fix the freezing when 
            // console.log('* has inited?', $(elem).hasClass('ui-autocomplete-input'));
            // once the $(elem).autocomplete() finished, 
            // the $(elem).hasClass('ui-autocomplete-input')) is always true
            // so we need to chech the label before running autocomplete
            if (has_ac) {
                return;
            }

            $(elem).on('focus', function(event) {
                console.log('* focus on', event.target);
                console.time('* search hints');
                $(this).autocomplete('search');
                console.timeEnd('* search hints');
            });
        });
        console.timeEnd('* update autocomplete');

        // console.log('* updated autocomplete');
    },

    _get_values_by_abbr: function(abbr, g_idx) {
        var v = {};

        for (const pid in this.vpp.$data.working_oc.data) {
            const paper = this.vpp.$data.working_oc.data[pid];
            if (!paper.is_selected) {
                continue;
            }
            // if (paper.is_selected) {
            //     // get the main values
            //     var val = paper.attrs.main[abbr];
            //     v[val] = 1;

            //     // get the values from 
            //     for (let i = 0; i < paper.attrs.other.length; i++) {
            //         const arm = paper.attrs.other[i];
            //         if (arm.hasOwnProperty(abbr)) {
            //             var arm_val = arm[abbr];
            //             v[arm_val] = 1;
            //         }
            //     }
            // }

            // 2021-04-24: the rule is different now
            // even the paper is not selected, we could still 
            // extract info and save for later use
            // get the main values

            // 2021-08-08: updated with group information
            // var val = paper.attrs.main['g'+g_idx][abbr];
            var val = '';

            // 2022-02-16: fix the empty group bug
            if (paper.attrs.main.hasOwnProperty('g'+g_idx)) {
                val = paper.attrs.main['g'+g_idx][abbr];
            } else {
                continue
            }
            v[val] = 1;

            // get the values from 
            for (let i = 0; i < paper.attrs.other.length; i++) {
                if (paper.attrs.other[i].hasOwnProperty('g'+g_idx)) {
                    // 2022-02-16: fix the empty group bug
                    const arm = paper.attrs.other[i]['g'+g_idx];
                    if (arm.hasOwnProperty(abbr)) {
                        var arm_val = arm[abbr];
                        v[arm_val] = 1;
                    }
                    
                } else {
                    continue
                }
                
            }
        }

        var distinct_vals = Object.keys(v);

        distinct_vals = distinct_vals.filter(function(item) {
            return item !== '' && item !== 'null' && item !== 'undefined'
        });
        distinct_vals.sort();

        // console.log('* got distinct_vals', distinct_vals)

        return distinct_vals;
    },

    /**
     * Set the highlight text to pid in the box
     * 
     * seq: null means `main`, 0 to x means item index in `other`
     */
     set_highlight_text_to_attr: function(highlight_text, attr_abbr) {
        console.log('* set_highlight_text_to_attr: ' + highlight_text + ' to ' + attr_abbr);

        // trim the text
        highlight_text = highlight_text.trim();

        // update the value for the specific paper
        // if (seq == null) {
        //     // it means this is the main track
        //     this.vpp.$data.working_oc.data[pid].attrs.main['g'+this.vpp.$data.working_paper_subg][attr_abbr] = highlight_text;
        // } else {
        //     // this means the value is for other arms
        //     this.vpp.$data.working_oc.data[pid].attrs.other[seq]['g'+this.vpp.$data.working_paper_subg][attr_abbr] = highlight_text;
        // }

        // 2021-08-15: just add to the working arm
        // this.get_working_arm_attrs()['g' + this.working_paper_subg][attr_abbr] = highlight_text;
        this.vpp.set_working_paper_arm_group_by_attr_value(attr_abbr, highlight_text);

        // update UI
        this.vpp.$forceUpdate();

        // 2021-08-18: scroll to that element for display
        // $('#wpc-input-' + attr_abbr)[0].scrollIntoView();
        $('#wpc-input-' + attr_abbr)
        .css('background-color', 'bisque')
        .effect(
            'shake',
            {
                direction: 'left',
                distance: 5,
                times: 3
            }
        ).animate({
            backgroundColor: 'white',
        });
    },

    update_ctx_menu: function(highlight_text, pid) {
        if (this.vpp.$data.working_oc == null) {
            // which means the oc is not selected
            return false;
        }

        // loop on the cate_attrs
        var html = [
            '<li class="menu-info">',
            '<div class="d-flex flex-row flex-align-center">',
                '<div class="mr-1" style="display:inline-block;"> <i class="fa fa-close"></i> ',
                'Highlighted </div>',
                '<div id="pan_ocpapers_ctx_menu_txt" title="'+highlight_text+'">'+highlight_text+'</div>',
            '</div>',
            '</li>'
        ];

        // this is for the main extracting
        // the last argument is null, means it's the main track
        html = this.__update_ctx_menu_html(html, highlight_text, pid, null);

        var n_arms = this.vpp.$data.working_oc.data[pid].n_arms;

        // 2021-08-30: since we use working_arm to decide, no need to have this
        // this is for the other extracting (i.e., multiple arms)
        // if (n_arms > 2) {
        //     html.push('<li class="ui-state-disabled menu-header"><div>Other Arms</div></li>');
            
        //     for (let a = 0; a < n_arms - 2; a++) {
        //         html.push('<li class="menu-item"><div>Comp '+(a+2)+'</div><ul>');
        //         html = this.__update_ctx_menu_html(html, highlight_text, pid, a);
        //         html.push('</ul></li>')
        //     }
        // }

        // put the new html into box
        $('#pan_ocpapers_ctx_menu').html(
            html.join('')
        );
    },

    __update_ctx_menu_html: function(html, highlight_text, pid, seq) {

        for (let i = 0; i < this.vpp.working_oc.meta.cate_attrs.length; i++) {

            const cate = this.vpp.working_oc.meta.cate_attrs[i];

            // put a new cate
            html.push('<li class="ui-state-disabled menu-header"><div>'+cate.name+'</div></li>');

            var flag_has_shown_attr = false;
            for (let j = 0; j < cate.attrs.length; j++) {
                const attr = cate.attrs[j];
                
                if (attr.subs == null) {
                    var is_show = this.vpp.is_show_attr(attr.abbr);
                    if (is_show) {
                        html.push(
                        '<li class="menu-item">' +
                            '<div onclick="pan_ocpapers.set_highlight_text_to_attr(\''+highlight_text+'\', \''+attr.abbr+'\')">' +
                            attr.name +
                            '</div>' +
                        '</li>'
                        );
                        flag_has_shown_attr = true;
                    }
                } else {
                    for (let k = 0; k < attr.subs.length; k++) {
                        const sub = attr.subs[k];
                        if (this.vpp.is_show_attr(sub.abbr)) {
                            html.push(
                            '<li class="menu-item">' +
                                '<div onclick="pan_ocpapers.set_highlight_text_to_attr(\''+highlight_text+'\', \''+sub.abbr+'\')">' +
                                attr.name + ' - ' + sub.name +
                                '</div>' +
                            '</li>'
                            );
                            flag_has_shown_attr = true;
                        }
                    }
                }
            }

            if (flag_has_shown_attr) {
                //
            } else {
                html.pop();
            }
            
        }

        return html;
    },

    show_ctx_menu: function(top, left) {
        // console.log('* show ctx menu at top:', top, 'left:', left);

        var win_width = $(document.body).width();
        var win_height = $(document.body).height();
        console.log('* win w:', win_width, 'h:', win_height);

        // generate the menu first
        $("#pan_ocpapers_ctx_menu").css({
            position: 'absolute',
            display: "block",
            top: -5000,
            left: -5000
        }).addClass("show").menu();
        $("#pan_ocpapers_ctx_menu").menu('refresh');

        // 2021-08-17: set to auto to get the actual height
        $("#pan_ocpapers_ctx_menu").css('height', 'auto');

        // fix the top and left 
        var box_width = $('#pan_ocpapers_ctx_menu').width();
        var box_height = $('#pan_ocpapers_ctx_menu').height();
        console.log('* ctx_menu w:', box_width, 'h:', box_height);

        // create a new style for the menu
        var style = {
            position: 'absolute',
            display: "block",
        };
        // 2021-08-16: fix the very large box height
        if (box_height > win_height) {
            box_height = win_height - 150;
            style.height = box_height;
        }
        // fix the left and top to avoid showing outside of window
        if (left + box_width > win_width) {
            left = win_width - box_width;
        }
        if (top + box_height > win_height) {
            top = win_height - box_height;
        }
        style.left = left;
        style.top = top;
        console.log('* adjusted show ctx menu at top:', top, 'left:', left);

        // display the menu
        $("#pan_ocpapers_ctx_menu").css(style);

        // bind other event
        $('#pan_ocpapers_ctx_menu .ui-menu-item').on('click', function() {
            $("#pan_ocpapers_ctx_menu").hide();
        });
    },

    hide_ctx_menu: function() {
        $("#pan_ocpapers_ctx_menu").hide();
    }
});