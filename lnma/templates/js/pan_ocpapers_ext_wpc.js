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
        var abbr = 'itable';
        var pid = this.working_paper.pid;

        // first, try to get the latest itable
        srv_extractor.get_pdata_in_extract(
            project_id,
            abbr,
            pid,
            function(data) {
                console.log('* got itable pdata:', data)
                // then, with the itable, try to fill?
                pan_ocpapers.fill_working_paper_attrs(
                    data
                );
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

    get_working_arm_attrs: function() {
        if (this.working_paper_arm == null) {
            return this.working_oc.data[this.working_paper.pid].attrs.main;
        } else {
            return this.working_oc.data[this.working_paper.pid].attrs.other[
                this.working_paper_arm
            ];
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
        // so, there are some pairs
        // from -> to
        // and currently, we don't know what 
    },

    /**
     * Update the auto-complete
     */
    update_autocomplete: function() {
        $('.input-auto-complete').each(function(idx, elem) {
            var abbr = $(elem).attr('abbr');
            var values = pan_ocpapers._get_values_by_abbr(abbr);

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
                    var pid = pan_ocpapers.vpp.$data.working_paper.pid;
                    var val = ui.item.value;

                    // set the value
                    // pan_ocpapers.vpp.$data.working_oc.data[pid].attrs.main[abbr] = val;
                    console.log('* selected [', val, '] for', abbr, 'of', pid);

                    // 2021-04-24: finally fixed this issue!!!
                    // the working arm may be main or other,
                    // need to use the get_working_arm_attrs() to get the current arm
                    // set the value to the working arm
                    pan_ocpapers.vpp.get_working_arm_attrs()[abbr] = val;
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

    _get_values_by_abbr: function(abbr) {
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
            var val = paper.attrs.main[abbr];
            v[val] = 1;

            // get the values from 
            for (let i = 0; i < paper.attrs.other.length; i++) {
                const arm = paper.attrs.other[i];
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
     set_highlight_text_to_attr: function(highlight_text, pid, attr_abbr, seq) {
        console.log('* set_highlight_text_to_attr: ' + highlight_text + ', ' + pid + ', ' + attr_abbr + ', ' + seq);

        // update the value for the specific paper
        if (seq == null) {
            // it means this is the main track
            this.vpp.$data.working_oc.data[pid].attrs.main[attr_abbr] = highlight_text;
        } else {
            // this means the value is for other arms
            this.vpp.$data.working_oc.data[pid].attrs.other[seq][attr_abbr] = highlight_text;
        }
        // update UI
        this.vpp.$forceUpdate();
    },

    update_ctx_menu: function(highlight_text, pid) {
        if (this.vpp.$data.working_oc == null) {
            // which means the oc is not selected
            return false;
        }

        // loop on the cate_attrs
        var html = [
            '<li class="menu-info"><div>',
                '<i class="fa fa-close"></i> ',
                'Highlighted <b id="pan_ocpapers_ctx_menu_txt">'+highlight_text+'</b> is:',
            '</div></li>'
        ];

        // this is for the main extracting
        // the last argument is null, means it's the main track
        html = this.__update_ctx_menu_html(html, highlight_text, pid, null);

        var n_arms = this.vpp.$data.working_oc.data[pid].n_arms;

        // this is for the other extracting (i.e., multiple arms)
        if (n_arms > 2) {
            html.push('<li class="ui-state-disabled menu-header"><div>Other Arms</div></li>');
            
            for (let a = 0; a < n_arms - 2; a++) {
                html.push('<li class="menu-item"><div>Arm '+(a+2)+'</div><ul>');
                html = this.__update_ctx_menu_html(html, highlight_text, pid, a);
                html.push('</ul></li>')
            }
        }

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
                            '<div onclick="pan_ocpapers.set_highlight_text_to_attr(\''+highlight_text+'\', \''+pid+'\', \''+attr.abbr+'\', '+seq+')">' +
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
                                '<div onclick="pan_ocpapers.set_highlight_text_to_attr(\''+highlight_text+'\', \''+pid+'\', \''+sub.abbr+'\', '+seq+')">' +
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
        // console.log('* win w:', win_width, 'h:', win_height);

        // generate the menu first
        $("#pan_ocpapers_ctx_menu").css({
            position: 'absolute',
            display: "block",
            top: -5000,
            left: -5000
        }).addClass("show").menu();
        $("#pan_ocpapers_ctx_menu").menu('refresh');

        // fix the top and left 
        var box_width = $('#pan_ocpapers_ctx_menu').width();
        var box_height = $('#pan_ocpapers_ctx_menu').height();
        // console.log('* box w:', box_width, 'h:', box_height);

        if (left + box_width > win_width) {
            left = win_width - box_width;
        }
        if (top + box_height > win_height) {
            top = win_height - box_height;
        }
        console.log('* adjusted show ctx menu at top:', top, 'left:', left);

        // display the menu
        $("#pan_ocpapers_ctx_menu").css({
            position: 'absolute',
            display: "block",
            top: top,
            left: left
        });

        // bind other event
        $('#pan_ocpapers_ctx_menu .ui-menu-item').on('click', function() {
            $("#pan_ocpapers_ctx_menu").hide();
        });
    },

    hide_ctx_menu: function() {
        $("#pan_ocpapers_ctx_menu").hide();
    }
});