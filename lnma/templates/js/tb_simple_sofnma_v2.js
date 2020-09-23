/*
 * Sof Table NMA
 */

var tb_simple_sofnma = {
    vpp: null,
    vpp_id: '#tb_simple_sofnma',

    default_comparator: null,
    default_external_base: 100,
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
                baseline: 1000,
                external_risk_calculated: 10,
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
                    if (!r.oc.treats.hasOwnProperty(t)) {
                        // this treat is not available in this study
                        return null;
                    } else {
                        return r.oc.treats[t].rank;
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

                    if (r.which_ACR.use_which_val == 'internal') {
                        // which means it's raw data with
                        return r.oc.treats[t].event / r.oc.treats[t].total;
                    }
                    if (r.which_ACR.use_which_val == 'external') {
                        // which means it's raw or pre
                        return r.which_ACR.external_val / this.baseline;
                    }
                },

                get_ACR_txt: function(r, t) {
                    var ACR = this.get_ACR(r, t);
                    if (ACR == null) {
                        // it means no available data for this treat
                        return 'NA';
                    } else {
                        return Math.round(ACR * this.baseline) + ' per ' + this.baseline;
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
                    return SRVC.toFixed(1) + ' months';
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

                get_cie: function(oc_name, comparator, treatment) {
                    return 0;
                    // return oc_dict[oc_name].cetable[comparator][treatment].cie);
                },

                get_cie_rob: function(oc_name, comparator, treatment) {
                    return 0;
                    // return oc_dict[oc_name].cetable[comparator][treatment].cie_rob);
                },

                get_cie_inc: function(oc_name, comparator, treatment) {
                    return 0;
                    // return oc_dict[oc_name].cetable[comparator][treatment].cie_inc);
                },

                get_cie_ind: function(oc_name, comparator, treatment) {
                    return 0;
                    // return oc_dict[oc_name].cetable[comparator][treatment].cie_ind);
                },

                get_cie_imp: function(oc_name, comparator, treatment) {
                    return 0;
                    // return oc_dict[oc_name].cetable[comparator][treatment].cie_imp);
                },

                get_pub_bia: function(oc_name, comparator, treatment) {
                    return 0;
                    // return oc_dict[oc_name].cetable[comparator][treatment].pub_bia);
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

                    if (v < 1) {
                        return 'cie-bene-2';
                    } else if ( v > 1) {
                        return 'cie-harm-2';
                    } else {
                        return 'cie-nner-2';
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

                    tb_simple_sofnma.show_detail(oc_name, treat, this.comparator);
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

    show_detail: function(oc_name, treat, comparator) {
        $(this.vpp_id + '_detail').dialog({
            width: 600
        });
    },

    make_oc_r: function(oc_name) {
        var oc = this.data.oc_dict[oc_name];

        var r = {
            oc: oc,
            which_ACR: {
                // internal is available only when data type is raw
                // pre data won't have this option
                has_internal: oc['oc_datatype'] == 'raw',
                // the default value
                use_which_val: oc['oc_datatype'] == 'raw'? 'internal':'external',
                // the external value
                external_val: tb_simple_sofnma.default_external_base,
                // decide which internal to use
                use_internal_avg: true,
                use_internal_min: false,
                use_internal_max: false
            },
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