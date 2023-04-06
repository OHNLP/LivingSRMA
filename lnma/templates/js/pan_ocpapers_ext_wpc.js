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

    // working piece
    working_piece: null,

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
            3: "3.3 If N/PN/NI to 3.2: Could missingness in the outcome depend on its true value?",
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
    // Basic function to show/hide
    /////////////////////////////////////////////////////
    show: function() {
        this.show_working_paper_pan = true;
    },

    hide: function() {
        this.show_working_paper_pan = false;
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

    set_has_change_unsaved: function() {
        this.has_saved = false;
    },

    set_has_change_saved: function() {
        this.has_saved = true;
    },

    confirm_drop_unsaved_changes: function() {
        if (this.has_saved) {
            // ok, it means no issue with previous
            return true;
        } else {
            var ret = window.confirm('The extraction for ['+ this.working_oc.meta.category+'|'+ this.working_oc.meta.full_name +'] may be changed and the changes are not saved yet. Are you sure to ignore the unsaved changes on ['+this.working_oc.meta.category+'|'+this.working_oc.meta.full_name+'] and work on other extraction?');

            if (ret) {
                // ok just ignore
                this.set_has_change_saved();
                return true;

            } else {
                // cannot skip
                return false;
            }
        }
    },
    

    confirm_close_wpc: function() {

    },

    on_change_input_value: function(event) {
        // no matter what happens, trigger this event
        // console.log('* changed any input', event);
        this.set_has_change_unsaved();
    },

    save_working_paper_extraction: function() {
        var pid = this.working_paper.pid;
        var oc = this.working_oc;

        this.saving_start();

        // 2023-01-28: a speciall rule for itable update
        if (this.working_oc.oc_type == 'itable') {
            // maybe need to update to update the oc info
            if (!this.hasOwnProperty('itable')) {
                // ??? why?
            } else {
                if (this.hasOwnProperty('working_piece'))
                // ok, using the current piece to update
                // get a copy
                this.itable.data[pid] = JSON.parse(JSON.stringify(this.working_piece.data));
            }
        }

        // a special rule for extract outcome page
        if (this.page_name == 'by_oc') {
            // which means user is extracting on the by_outcome page
            // need to copy the piece to the working oc
            this.working_oc.data[pid] = JSON.parse(JSON.stringify(
                this.working_piece.data
            ));
        }

        // 2023-01-28: Use piece to update
        srv_extractor.update_extract_piece(
            this.working_piece,
            function(data) {
                // the data contain a paer
                console.log('* update_extract_piece returns:', data);

                jarvis.toast('Saved [' + data.data.piece.pid + '] extraction with current extraction');
                pan_ocpapers.vpp.saving_end();
            }
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

    set_n_arms: function(flag_copy_main, flag_reset_working_arm, flag_force_update) {
        if (typeof(flag_copy_main) == 'undefined') {
            flag_copy_main = false;
        }
        if (typeof(flag_reset_working_arm) == 'undefined') {
            flag_reset_working_arm = true;
        }
        if (typeof(flag_force_update) == 'undefined') {
            flag_force_update = true;
        }
        // notify unsaved changes first
        this.set_has_change_unsaved();

        // var n_arms = parseInt(
        //     this.working_oc.data[this.working_paper.pid].n_arms
        // );
        var n_arms = parseInt(
            this.working_piece.data.n_arms
        );
        console.log('* set n_arms to', n_arms);

        // update the other to match the number
        // this.working_oc.data[this.working_paper.pid] = srv_extractor.set_n_arms(
        //     this.working_oc.data[this.working_paper.pid], 
        //     n_arms
        // );
        
        // 2023-03-30: update to working_piece
        this.working_piece.data = srv_extractor.set_n_arms(
            this.working_piece.data,
            n_arms,
            flag_copy_main
        );

        // update current working arm to main
        if (flag_reset_working_arm) {
            this.switch_working_arm(null);
        }
        
        if (flag_force_update) {
            this.$forceUpdate();
        }
    },

    switch_working_arm: function(arm_idx) {
        console.log('* switch_working_arm', arm_idx);

        // 2023-03-30: this can be tricky for multi-arm study
        // the working_paper_arm may NOT exist
        // so need to ensure other arms are available before switch
        if (arm_idx == null) {
            // ok, nothing, just switch to main
        } else if ((arm_idx+1) > this.working_piece.data.attrs.other.length) {
            // which means the target arm is not there yet???
            // usually it won't happen, but sometimes ...
            // due to import issue or other issues
            // working_piece.data.attrs.other may NOT exist
            // now need to update the data
            console.log('* missing other arms in this piece');
            this.set_n_arms(false, false);
            // then the piece is updated, now it should be fine to get data
        }

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
        // if (this.working_paper_arm == null) {
        //     return this.working_oc.data[this.working_paper.pid].attrs.main;
        // } else {
        //     return this.working_oc.data[this.working_paper.pid].attrs.other[this.working_paper_arm];
        // }
        if (this.working_paper_arm == null) {
            return this.working_piece.data.attrs.main;
        } else {
            return this.working_piece.data.attrs.other[this.working_paper_arm];
        }
    },

    set_working_paper_arm_by_group_attr_value: function(g_idx, abbr, value) {
        var old_val = this.get_working_arm_attrs()['g'+g_idx][abbr];
        this.get_working_arm_attrs()['g'+g_idx][abbr] = value;
        console.log('* set value ' + old_val + ' -> ' + this.get_working_arm_attrs()['g'+g_idx][abbr]);
        
        // notify changed
        this.set_has_change_unsaved();

        this.$forceUpdate();
    },

    set_working_paper_arm_group_by_attr_value: function(abbr, value) {
        var old_val = this.get_working_arm_attrs()['g'+this.working_paper_subg][abbr];
        this.get_working_arm_attrs()['g'+this.working_paper_subg][abbr] = value;
        console.log('* set wk_pp_arm_group value ' + old_val + ' -> ' + value);
        // notify changed
        this.set_has_change_unsaved();
    },

    set_working_paper_arm_allgroups_by_attr_value: function(abbr, value) {
        for (let i = 0; i < this.working_oc.meta.sub_groups.length; i++) {        
            this.get_working_arm_attrs()['g'+i][abbr] = value;
        }
        // notify changed
        this.set_has_change_unsaved();
    },


    clear_working_arm_attr: function(g_idx, abbr) {
        this.get_working_arm_attrs()['g'+g_idx][abbr] = '';
        this.set_has_change_unsaved();
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
                    pan_ocpapers.vpp.set_has_change_unsaved();

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
        this.vpp.set_working_paper_arm_group_by_attr_value(
            attr_abbr, 
            highlight_text
        );

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
        html = this.__update_ctx_menu_html(
            html, 
            highlight_text, 
            pid, 
            null
        );

        // 2023-04-06: use piece to get data
        var n_arms = this.vpp.$data.working_piece.data.n_arms;

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
        // 2023-04-06: to generate the context menu
        // need to check the current working oc and items to be extracted
        for (let i = 0; i < this.vpp.working_oc.meta.cate_attrs.length; i++) {
            // get the categories from working_oc
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
    },

    close_wpc: function() {
        if (this.vpp.confirm_drop_unsaved_changes()) {
            // ok, nothing happens here
        } else {
            return;
        }

        // then you can close now
        this.vpp.hide();
        pan_collector.hide();
    }
});