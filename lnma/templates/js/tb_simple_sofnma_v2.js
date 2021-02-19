/*
 * Sof Table NMA
 */

var tb_simple_sofnma = {
    vpp: null,
    vpp_id: '#tb_simple_sofnma',

    default_comparator: null,
    default_external_val: 0,
    default_external_base: 1000,
    default_measure: '',
    measure_list: [],

    color_scale: d3.scaleLinear()
        .domain([0, 1, 3])
        .range(['#78b787', 'white', '#ff0000']),

    init: function(data) {
        this.data = data;

        // get all treats
        var default_oc_name = data.oc_list[0]['oc_names'][0];
        var treat_list = data.treat_list;
        if (this.default_comparator == null || this.default_comparator == '') {
            this.default_comparator = treat_list[0];
        }
        var default_treat = treat_list[1];

        // get all oc
        var rs = {};
        for (var i = 0; i < data.oc_list[0].oc_names.length; i++) {
            var oc_name = data.oc_list[0].oc_names[i];
            var r = this.make_oc_r(oc_name);
            rs[oc_name] = r;
        }

        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                measure: this.default_measure,
                measure_list: this.measure_list,
                baseline: this.default_external_base,
                show_survival: 'no',
                survival_value_type: 'avg',
                detail: {
                    oc_name: default_oc_name,
                    treat: default_treat
                },
                comparator: this.default_comparator,
                treat_list: treat_list,
                oc_dict: this.data.oc_dict,
                oc_list: this.data.oc_list,
                set_ctrl_oc_name: default_oc_name,
                rs: rs
            },
            methods: {
                // get the UI text
                get_a_measure: function(r) {
                    // if current specific measure is not available in this oc
                    // use the first one instead
                    if (r.oc.lgtable.hasOwnProperty(this.measure)) {
                        return this.measure;
                    } else {
                        return r.oc.oc_measures[0];
                    }
                },

                get_rank: function(r, t) {
                    if (r.oc.treats.hasOwnProperty(t)) {
                        var measure = this.get_a_measure(r);
                        return r.oc.rktable[measure][t].rank;
                    } else {
                        // this treat is not available in this study
                        return null;
                    }
                },

                get_rank_txt: function(r, t) {
                    var rank = this.get_rank(r, t);
                    if (rank == null) {
                        return 'NA';
                    } else {
                        return 'Rank ' + rank;
                    }
                },

                get_ACR: function(r, t) {
                    // the t is a treat
                    // t may be missing in this r
                    if (!r.oc.treats.hasOwnProperty(t)) {
                        // this treat is not available in this study
                        return null;
                    }

                    if (r.oc.treats[t].which_ACR.use_which_val == 'internal') {
                        if (r.oc.treats.hasOwnProperty(t)) {
                            if (r.oc.treats[t].has_internal_val) {

                                if (r.oc.oc_datatype == 'raw') {
                                    return r.oc.treats[t].event / r.oc.treats[t].total; 
                                } else {
                                    return r.oc.treats[t].internal_val / 1000;
                                }

                            } else {
                                return 0.1;
                            }

                        } else {
                            return null;
                        }

                    } else {
                        return r.oc.treats[t].which_ACR.external_val / this.baseline;
                    }

                    // if (r.which_ACR.use_which_val == 'internal') {
                    //     // which means it's raw data with
                    //     return r.oc.treats[t].event / r.oc.treats[t].total;
                    // }
                    // if (r.which_ACR.use_which_val == 'external') {
                    //     // which means it's raw or pre
                    //     if (r.oc.treats.hasOwnProperty(t)) {
                    //         if (r.oc.treats[t].has_external_val) {
                    //             return r.oc.treats[t].external_val / 1000;
                    //         } else {
                    //             return r.which_ACR.external_val / this.baseline;
                    //         }
                    //     } else {
                    //         return null;
                    //     }
                    //     // return r.which_ACR.external_val / this.baseline;
                    // }
                },

                get_ACR_txt: function(r, t) {
                    var ACR = this.get_ACR(r, t);
                    if (ACR == null) {
                        // it means no available data for this treat
                        return 'NA';
                    } else {
                        if (r.oc.treats[t].which_ACR.use_which_val == 'internal') {
                            return Math.round(ACR * this.baseline) + ' per ' + this.baseline;
                        } else {
                            return Math.round(ACR * this.baseline) + ' per ' + this.baseline;
                            // return Math.round(ACR * this.baseline) + ' per ' + this.baseline + '<br>' +
                                // '('+r.oc.treats[t].which_ACR.use_which_val+')';
                        }
                    }
                },

                get_CIR: function(r, c, t, obj) {
                    // calculate the CIR based on measure
                    // r is the oc_r
                    // obj: sm, lw, up
                    // c is comparator, t is treatment
                    var ACR = this.get_ACR(r, c);
                    if (ACR == null) {
                        // if ACR is not available, no need to calcuate others
                        return null;
                    }

                    // get an available measure for this oc
                    var measure = this.get_a_measure(r);
                    // v is the value of the sm/lw/up of this measure
                    if (!r.oc.lgtable[measure].hasOwnProperty(t)) {
                        // this t is not available for this oc
                        return null;
                    }
                    var v = r.oc.lgtable[measure][c][t][obj];

                    if (measure == 'OR') {
                        var a = ACR * v;
                        var b = 1 - ACR;
                        var c = a + b;
                        var d = a / c;
                        return d;
                    } else if (measure == 'RR') {
                        var a = ACR * v;
                        return a;
                    } else if (measure == 'HR') {
                        var a = 1 - ACR;
                        var b = Math.log(a);
                        var c = b * v;
                        var d = Math.exp(c);
                        var e = 1 - d;
                        return e;
                    }
                },

                get_CIR_txt: function(r, c, t, obj) {
                    var CIR = this.get_CIR(r, c, t, obj);
                    if (CIR == null) {
                        // it means no available data for this treat
                        return 'NA';
                    } else {
                        return Math.round(CIR * this.baseline) + ' per ' + this.baseline;
                    }
                },

                get_ARD: function(r, c, t, obj) {
                    // calculate the ARD based on measure
                    // r is the oc_r
                    // obj: sm, lw, up
                    // c is comparator, t is treatment

                    var ACR = this.get_ACR(r, c);
                    if (ACR == null) {
                        // if ACR is not available, no need to calcuate others
                        return null;
                    }
                    var CIR = this.get_CIR(r, c, t, obj);
                    if (CIR == null) {
                        // if CIR is not available, no need to calcuate others
                        return null;
                    }

                    // get an available measure for this oc
                    var measure = this.get_a_measure(r);
                    // v is the value of the sm/lw/up of this measure
                    var v = r.oc.lgtable[measure][c][t][obj];

                    if (measure == 'OR') {
                        var ARD = ACR - CIR;
                        return ARD;
                    } else if (measure == 'RR') {
                        var a = ACR * (1 - v);
                        return a;
                    } else if (measure == 'HR') {
                        var ARD = ACR - CIR;
                        return ARD;
                    }
                },

                get_ARD_txt: function(r, c, t, obj) {
                    var ARD = this.get_ARD(r, c, t, obj);
                    if (ARD == null) {
                        return 'NA';
                    }
                    var txt = ' fewer';
                    if (ARD < 0) {
                        txt = ' more';
                    }
                    return Math.abs(Math.round(ARD * this.baseline)) + txt;
                },

                get_ARDp: function(r, c, t, obj) {
                    var ARD = this.get_ARD(r, c, t, obj);
                    if (ARD == null) {
                        return null;
                    }
                    var ARDp = 100 * ARD;
                    return ARDp;
                },

                get_ARDp_txt: function(r, c, t, obj) {
                    var ARDp = this.get_ARDp(r, c, t, obj);
                    if (ARDp == null) {
                        return 'NA';
                    }
                    var txt = ' fewer';
                    if (ARDp < 0) {
                        txt = ' more';
                    }
                    return Math.abs(ARDp).toFixed(1) + '%' + txt;
                },

                /***********************************************
                 * Measure of Effects Related
                 ***********************************************/

                
                /**
                 * Get the effect of a measure of outcome
                 * @date 2020-09-23
                 * @param {any} oc_name
                 * @param {any} m measure name, e.g., OR, RR, HR
                 * @param {any} c comparator
                 * @param {any} t treatment
                 * @param {any} obj sm/lw/up
                 * @returns {any}
                 */
                get_effect: function(oc_name, m, c, t, obj) {
                    var r = this.rs[oc_name];

                    if (!r.oc.lgtable.hasOwnProperty(m)) {
                        // this oc doesn't have this measure
                        return null;
                    }

                    if (!r.oc.lgtable[m].hasOwnProperty(c)) { 
                        // this oc doesn't have this c
                        return null;
                    }

                    if (!r.oc.lgtable[m][c].hasOwnProperty(t)) { 
                        // this oc doesn't have this t
                        return null;
                    }

                    var e =  r.oc.lgtable[m][c][t][obj];
                    return e;
                },

                get_effect_txt: function(oc_name, m, c, t, obj) {
                    var e = this.get_effect(oc_name, m, c, t, obj);

                    if (e == null) {
                        return 'NA';
                    }

                    return e.toFixed(2);
                },

                /**
                 * Get the treat obj of outcome
                 * @date 2020-09-23
                 * @param {any} oc_name
                 * @param {any} t treatment name
                 * @returns {any}
                 */
                get_treat: function(oc_name, t) {
                    var r = this.rs[oc_name];
                    if (!r.oc.treats.hasOwnProperty(t)) {
                        return null;
                    }
                    return r.oc.treats[t];
                },

                get_treat_attr_txt: function(oc_name, t, a) {
                    var treat = this.get_treat(oc_name, t);
                    if (treat == null) {
                        return 'NA';
                    }
                    return treat[a];
                },

                get_n_stus: function(oc_name, t) {
                    var r = this.rs[oc_name];
                    if (!r.oc.treats.hasOwnProperty(t)) {
                        return null;
                    }
                    return r.oc.treats[t].n_stus;
                },

                get_n_stus_text: function(oc_name, t) {
                    var n_stus = this.get_n_stus(oc_name, t);
                    if (n_stus == null) {
                        return 'NA';
                    }
                    return n_stus;
                },

                /***********************************************
                 * Survival Related
                 ***********************************************/

                // get survival in control
                get_SRVC: function(r, c) {
                    if (!r.oc.treats.hasOwnProperty(c)) {
                        // this comparator is not available in this oc
                        return null;
                    }
                    if (!r.oc.treats[c].has_survival_data) {
                        // this oc doesn't have survival data
                        return null;
                    }
                    var SRVC = r.oc.treats[c].survival_in_control[this.survival_value_type];
                    return SRVC;
                },

                get_SRVC_txt: function(r, c) {
                    var SRVC = this.get_SRVC(r, c);
                    if (SRVC == null) {
                        return 'NA';
                    }
                    return SRVC.toFixed(1) + ' (mo)';
                },

                get_SRVI: function(r, c, t, obj) {
                    var SRVC = this.get_SRVC(r, c);
                    if (SRVC == null) {
                        // this comparator doesn't have survival data
                        return null;
                    }
                    // currently, only HR has survival data
                    var measure = 'HR';
                    if (!r.oc.lgtable.hasOwnProperty(measure)) {
                        // this oc doesn't have this measure
                        return null;
                    }
                    // v is the value of the sm/lw/up of this measure
                    var v = r.oc.lgtable[measure][c][t][obj];
                    // get the survival in 
                    var SRVI = (1 / v) * SRVC;
                    return SRVI;
                },

                get_SRVI_txt: function(r, c, t, obj) {
                    var SRVI = this.get_SRVI(r, c, t, obj);
                    if (SRVI == null) {
                        return 'NA';
                    }
                    return SRVI.toFixed(1) + ' (mo)';
                },

                get_SRVD: function(r, c, t, obj) {
                    var SRVC = this.get_SRVC(r, c);
                    var SRVI = this.get_SRVI(r, c, t, obj);
                    
                    if (SRVC == null) { return null; }
                    if (SRVI == null) { return null; }

                    var SRVD = SRVC - SRVI;
                    return SRVD;
                },

                get_SRVD_txt: function(r, c, t, obj) {
                    var SRVD = this.get_SRVD(r, c, t, obj);
                    if (SRVD == null) {
                        return 'NA';
                    }
                    var txt = '';
                    if (SRVD < 0) {
                        txt = ' more';
                    } else if (SRVD > 0) {
                        txt = ' fewer';
                    } else {
                        txt = '';
                    }
                    return Math.abs(SRVD).toFixed(1) + ' (mo)' + txt;
                },

                /***********************************************
                 * Certainty in evidence Related
                 ***********************************************/

                get_cet: function(oc_name, c, t) {
                    var r = this.rs[oc_name];
                    if (!r.oc.cetable.hasOwnProperty(c)) {
                        return null;
                    }
                    if (!r.oc.cetable[c].hasOwnProperty(t)) {
                        return null;
                    }
                    return r.oc.cetable[c][t];
                },

                get_cet_attr_val: function(oc_name, c, t, a) {
                    var cet = this.get_cet(oc_name, c, t);
                    if (cet == null) {
                        return 0;
                    }
                    return cet[a];
                },

                get_cet_attr_txt: function(oc_name, c, t, a) {
                    var cet_val = this.get_cet_attr_val(oc_name, c, t, a);
                    if (cet_val == 0) {
                        return 'NA';
                    }
                    if (a == 'cie') {
                        return jarvis.txt['CIE_TOT_' + cet_val];
                    } else if (a == 'pub_bia') {
                        return jarvis.txt['PUB_BIA_' + cet_val];
                    } else {
                        return jarvis.txt['CIE_VAL_' + cet_val];
                    }
                },

                // for UI
                get_grade_label: function(g) {
                    return jarvis.texts[g];
                },

                get_bg_color_class2: function(r, c, t, cie) {
                    var CIR = this.get_CIR(r, c, t);
                    if (CIR == null) {
                        // no value for this cell, just blank
                        return '';
                    }
                    
                    // get an available measure for this oc
                    var measure = this.get_a_measure(r);
                    // v is the value of the sm of this measure
                    var v = r.oc.lgtable[measure][c][t]['sm'];

                    if (this.show_survival == 'yes') {
                        var SRVI = this.get_SRVI(r, c, t, 'sm');
                        if (SRVI == null) {
                            // no survival data for this c or t
                            return '';
                        }
                    }
                    
                    if (r.oc.param.which_is_better == 'lower') {
                        if (v < 1) {
                            return 'cie-bene-' + cie;
                        } else if ( v > 1) {
                            return 'cie-harm-' + cie;
                        } else {
                            return 'cie-nner-' + cie;
                        }
                    } else {
                        if (v > 1) {
                            return 'cie-bene-' + cie;
                        } else if ( v < 1) {
                            return 'cie-harm-' + cie;
                        } else {
                            return 'cie-nner-' + cie;
                        }
                    }
                },

                get_bg_color_class: function(sm, cie) {
                    if (sm < 1) {
                        return 'cie-bene-' + cie;
                    } else if (sm > 1) {
                        return 'cie-harm-' + cie;
                    } else {
                        return 'cie-nner-' + cie;
                    }
                },

                flip_cell: function(oc_grade, r, cell) {
                    // first, find this oc in rs
                    if (this.rs[oc_grade].hasOwnProperty(r.name)) {
                        // flip this cell!
                        this.rs[oc_grade][r.name].is_show[cell] = 
                            !this.rs[oc_grade][r.name].is_show[cell];
                    } else {
                        // how can it be ???
                    }
                    this.$forceUpdate();
                },

                get_cieclr: function(sm, cie) {
                    if (sm < 1) {
                        return 'cie-bene-' + cie;
                    } else if (sm > 1) {
                        return 'cie-harm-' + cie;
                    } else {
                        return 'cie-nnor-' + cie;
                    }
                },

                show_detail: function(oc_name, treat) {
                    this.detail.oc_name = oc_name;
                    this.detail.treat = treat;
                    tb_simple_sofnma.show_detail();
                },

                show_ctrl_options: function(oc_name) {
                    this.set_ctrl_oc_name = oc_name;
                    tb_simple_sofnma.show_ctrl_options();
                },

                txt: function(t) {
                    return jarvis.txt[t];
                }
            },
        });
    },

    toggle_oc: function(oc_name) {
        // first, find this oc in rs
        if (this.vpp.rs.hasOwnProperty(oc_name)) {
            // if exists, remove
            delete this.vpp.rs[oc_name];
        } else {
            var oc = this.data.oc_dict[oc_name];
            // add this to list
            this.vpp.rs[oc_name] = oc;
        }

        // have to force update the view
        tb_simple_sofnma.vpp.$forceUpdate();
    },

    show_detail: function() {
        $(this.vpp_id + '_detail').dialog({
            width: 600
        });
    },

    show_ctrl_options: function() {
        $(this.vpp_id + '_ctrl_select').dialog({
            width: 300,
            my: 'left', 
            at: 'right'
        });
    },

    make_oc_r: function(oc_name) {
        var oc = this.data.oc_dict[oc_name];

        for (var t in oc.treats) {
            oc.treats[t]['which_ACR'] = {
                // the default value
                use_which_val: oc.treats[t].has_internal_val? 'internal':'external',
                // the external value
                external_val: tb_simple_sofnma.default_external_val,
                // decide which internal to use
                use_internal_avg: true,
                use_internal_min: false,
                use_internal_max: false
            };
        }

        var r = {
            oc: oc,
            // which_ACR: {
            //     // internal is available only when data type is raw
            //     // pre data won't have this option
            //     has_internal: oc['oc_datatype'] == 'raw',
            //     // the default value
            //     use_which_val: oc['oc_datatype'] == 'raw'? 'internal':'external',
            //     // the external value
            //     external_val: tb_simple_sofnma.default_external_base,
            //     // decide which internal to use
            //     use_internal_avg: true,
            //     use_internal_min: false,
            //     use_internal_max: false
            // },
            // for display setting
            is_show: {
                // show sm, study info
                sm: true,
                // show ARD, or ARD CI
                ARD: true,
                // show CIR, or CIR CI
                CIR: true
            }
        };

        return r;
    },

    clear: function() {

    },

    clear_all_oc: function() {
        for (var key in tb_simple_sofnma.vpp.rs) {
            if (tb_simple_sofnma.vpp.rs.hasOwnProperty(key)) {
                delete tb_simple_sofnma.vpp.rs[key];
            }
        }
        tb_simple_sofnma.vpp.$forceUpdate();
    }
};