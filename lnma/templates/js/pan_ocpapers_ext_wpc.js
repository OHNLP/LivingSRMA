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
    working_paper_subg: 0
});

// Extend the vpp methods
Object.assign(pan_ocpapers.vpp_methods, {
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

    save_working_paper_extraction: function() {
        var pid = this.working_paper.pid;
        var oc = this.working_oc;

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
        var n_arms = parseInt(this.working_oc.data[this.working_paper.pid].n_arms);
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
        
        this.$forceUpdate();
    },

    set_working_paper_arm_group_by_attr_value: function(abbr, value) {
        var old_val = this.get_working_arm_attrs()['g'+this.working_paper_subg][abbr];
        this.get_working_arm_attrs()['g'+this.working_paper_subg][abbr] = value;
        console.log('* set wk_pp_arm_group value ' + old_val + ' -> ' + value);
    },

    set_working_paper_arm_allgroups_by_attr_value: function(abbr, value) {
        for (let i = 0; i < this.working_oc.meta.sub_groups.length; i++) {        
            this.get_working_arm_attrs()['g'+i][abbr] = value;
        }
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
        $('.input-auto-complete').each(function(idx, elem) {
            var abbr = $(elem).attr('abbr');
            var g_idx = $(elem).attr('g_idx');
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

                    // 2021-04-24: finally fixed this issue!!!
                    // the working arm may be main or other,
                    // need to use the get_working_arm_attrs() to get the current arm
                    // set the value to the working arm
                    pan_ocpapers.vpp.get_working_arm_attrs()['g'+g_idx][abbr] = val;
                },

                change: function (e, ui) {
                    // console.log("changed!", e, ui);
                }

            }).on('focus', function(event) {
                $(this).autocomplete('search');
            });
        });
        console.log('* updated autocomplete');
    },

    _get_values_by_abbr: function(abbr, g_idx) {
        var v = {};

        for (const pid in this.vpp.$data.working_oc.data) {
            const paper = this.vpp.$data.working_oc.data[pid];
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

            var val = paper.attrs.main['g'+g_idx][abbr];
            v[val] = 1;

            // get the values from 
            for (let i = 0; i < paper.attrs.other.length; i++) {
                const arm = paper.attrs.other[i]['g'+g_idx];
                if (arm.hasOwnProperty(abbr)) {
                    var arm_val = arm[abbr];
                    v[arm_val] = 1;
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