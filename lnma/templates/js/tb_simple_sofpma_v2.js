/*
 * SoF Table PMA
 */
var tb_simple_sofpma = {
    vpp: null,
    vpp_id: '#tb_simple_sofpma',

    default_external_base: 100,
    default_measure: '',
    measure_list: [],

    init: function(data) {
        this.data = data;

        var rs = {};
        for (var i = 0; i < data.oc_list[0].oc_names.length; i++) {
            var oc_name = data.oc_list[0].oc_names[i];
            var r = this.make_oc_r(oc_name);
            rs[oc_name] = r;
        }
        console.log(rs);

        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                measure: this.default_measure,
                measure_list: this.measure_list,
                baseline: 1000,
                show_survival: 'yes',
                set_ctrl_oc_name: data.oc_list[0].oc_names[0],
                detail: {
                    cie: { oc_name: data.oc_list[0].oc_names[0] }
                },
                oc_dict: data.oc_dict,
                oc_list: data.oc_list,
                rs: rs
            },
            methods: {
                // get the UI text
                get_a_measure: function(r) {
                    if (r.oc.result.hasOwnProperty(this.measure)) {
                        return this.measure;
                    } else {
                        return r.oc.oc_measures[0];
                    }
                },

                // get survival in control
                get_SRVC: function(r) {
                    if (r.has_survival_data) {
                        return r.oc.survival_in_control;
                    } else {
                        return null;
                    }
                },

                get_SRVC_txt: function(r) {
                    if (r.has_survival_data) {
                        return this.get_SRVC(r).toFixed(1) + ' (mo)';
                    } else {
                        return 'NA';
                    }
                },

                get_SRVI: function(r, obj) {
                    if (r.has_survival_data) {
                        var hr = r.oc.result['HR'].random.model[obj];
                        var srvi = (1 / hr) * r.oc.survival_in_control;
                        return srvi;
                    } else {
                        return null;
                    }
                },

                get_SRVI_txt: function(r, obj) {
                    // obj could be
                    // sm, lower, upper
                    if (r.has_survival_data) {
                        var srvi = this.get_SRVI(r, obj);
                        return srvi.toFixed(1) + ' (mo)';
                    } else {
                        return 'NA';
                    }
                },

                get_SRVD: function(r, obj) {
                    var SRVC = this.get_SRVC(r);
                    var SRVI = this.get_SRVI(r, obj);
                    
                    if (SRVC == null) { return null; }
                    if (SRVI == null) { return null; }

                    var SRVD = SRVC - SRVI;
                    return SRVD;
                },

                get_SRVD_txt: function(r, obj) {
                    var SRVD = this.get_SRVD(r, obj);
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

                // calc the ACR, CIR, ARD
                get_ACR: function(r) {
                    if (r.which_ACR.use_which_val == 'internal') {
                        return r.Ec / r.Nc;
                    }
                    if (r.which_ACR.use_which_val == 'external') {
                        return r.which_ACR.external_val / this.baseline;
                    }
                },

                get_CIR: function(r, obj) {
                    // get the obj of this CIR
                    // obj could be
                    // sm, lower, upper
                    if (typeof(obj)=='undefined') {
                        obj = 'sm';
                    }
                    // val is the value of measure
                    // OR, RR, HR
                    var val = r.oc.result[this.get_a_measure(r)].random.model[obj];

                    // calculate the CIR based on measure
                    if (this.get_a_measure(r) == 'OR') {
                        var a = this.get_ACR(r) * val;
                        var b = 1 - this.get_ACR(r);
                        var c = a + b;
                        var d = a / c;
                        var e = d * this.baseline;
                        return d;
                    } else if (this.get_a_measure(r) == 'RR') {
                        var a = this.get_ACR(r) * val;
                        return a;
                    } else if (this.get_a_measure(r) == 'HR') {
                        var a = 1 - this.get_ACR(r);
                        var b = Math.log(a);
                        var c = b * val;
                        var d = Math.exp(c);
                        var e = 1 - d;
                        return e;
                    }
                },

                get_ARD: function(r, obj) {
                    // obj could be
                    // sm, lower, upper
                    if (typeof(obj)=='undefined') {
                        obj = 'sm';
                    }
                    var val = r.oc.result[this.get_a_measure(r)].random.model[obj];

                    // calc the ARD
                    if (this.get_a_measure(r) == 'OR') {
                        var ACR = this.get_ACR(r);
                        var CIR = this.get_CIR(r, obj);
                        var ARD = ACR - CIR;
                        return ARD;
                    } else if (this.get_a_measure(r) == 'RR') {
                        var a = this.get_ACR(r) * (1 - val);
                        return a;
                    } else if (this.get_a_measure(r) == 'HR') {
                        var ACR = this.get_ACR(r);
                        var CIR = this.get_CIR(r, obj);
                        var ARD = ACR - CIR;
                        return ARD;
                    }
                },

                get_ARD_txt: function(r, obj) {
                    var ARD = this.get_ARD(r, obj);
                    var txt = ' fewer';
                    if (ARD < 0) {
                        txt = ' more';
                    }
                    return Math.abs(Math.round(ARD * this.baseline)) + txt;
                },

                get_ARDp_txt: function(r, obj) {
                    var ARDp = 100 * this.get_ARD(r, obj);
                    var txt = ' fewer';
                    if (ARDp < 0) {
                        txt = ' more';
                    }
                    return Math.abs(ARDp).toFixed(1) + '%' + txt;
                },

                get_grade_label: function(g) {
                    return jarvis.texts[g];
                },

                flip_cell: function(r, cell) {
                    console.log(r);
                    // first, find this oc in rs
                    if (this.rs.hasOwnProperty(r.oc_name)) {
                        // flip this cell!
                        this.rs[r.oc_name].is_show[cell] = 
                            !this.rs[r.oc_name].is_show[cell];
                    } else {
                        // how can it be ???
                    }
                    this.$forceUpdate();
                },

                txt: function(t) {
                    return jarvis.txt[t];
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

                show_cie_detail: function(oc_name) {
                    this.detail.cie.oc_name = oc_name;
                    tb_simple_sofpma.show_cie_detail(oc_name);
                },

                show_ctrl_options: function(oc_name) {
                    this.set_ctrl_oc_name = oc_name;
                    tb_simple_sofpma.show_ctrl_options(oc_name);
                }
            },
        });
    },

    make_oc_r: function(oc_name) {
        var oc = this.data.oc_dict[oc_name];
        if (oc.stus.length == 0) {
            // this means no studies in this oc + grade 
            return;
        }
    
        // build the r for display
        var r = {
            oc: oc,
            oc_name: oc.oc_name,
            oc_fullname: oc.oc_fullname,
            // for the raw
            Et: oc.Et,
            Nt: oc.Nt,
            Ec: oc.Ec,
            Nc: oc.Nc,
            // for the pre
            TE: oc.TE,
            lowerci: oc.lowerci,
            upperci: oc.upperci,
            has_survival_data: oc.survival_in_control > 0,
            // general data
            n_stu: oc.stus.length,
            which_ACR: {
                // internal is available only when data type is raw
                // pre data won't have this option
                has_internal: oc['oc_datatype'] == 'raw',
                // the default value
                use_which_val: oc['oc_datatype'] == 'raw'? 'internal':'external',
                // the external value
                external_val: oc['external_val'],
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
        }
        return r;
    },

    toggle_oc: function(oc_name) {
        // first, find this oc in rs
        if (this.vpp.rs.hasOwnProperty(oc_name)) {
            // if exists, remove
            delete this.vpp.rs[oc_name];
        } else {
            // make a r for this oc
            var r = this.make_oc_r(oc_name);
            // add this to list
            this.vpp.rs[oc_name] = r;
        }

        // have to force update the view
        tb_simple_sofpma.vpp.$forceUpdate();
    },

    clear: function() {

    },

    clear_all_oc: function() {
        for (var key in tb_simple_sofpma.vpp.rs) {
            if (tb_simple_sofpma.vpp.rs.hasOwnProperty(key)) {
                delete tb_simple_sofpma.vpp.rs[key];
            }
        }
        tb_simple_sofpma.vpp.$forceUpdate();
    },

    show_cie_detail: function(oc_name) {
        $(this.vpp_id + '_cie_detail').dialog({
            width: 400
        });
    },

    show_ctrl_options: function(oc_name) {
        $(this.vpp_id + '_ctrl_select').dialog({
            width: 300,
            my: 'left', 
            at: 'right'
        });
    }
};