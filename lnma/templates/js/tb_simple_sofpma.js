/*
 * SoF Table PMA
 */
var tb_simple_sofpma = {
    vpp: null,
    vpp_id: '#tb_simple_sofpma',

    default_measure: 'OR',
    measure_list: [
        { abbr: 'OR', name: 'Odds Ratio (OR)' },
        { abbr: 'RR', name: 'Risk Ratio (RR)' },
        { abbr: 'HR', name: 'Hazard Ratio (RR)' },
    ],

    init: function(data) {
        this.data = data;

        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                measure: this.default_measure,
                measure_list: this.measure_list,
                baseline: 1000,
                external_risk_calculated: 10,
                use_internal_baseline: true,
        
                detail: {
                    cie: { ae_name: data.ae_list[0].ae_names[0] }
                },
                ae_dict: data.ae_dict,
                ae_list: data.ae_list,
                rs: {}
            },
            methods: {
                get_ACR: function(r) {
                    if (this.use_internal_baseline) {
                        return r.Ec / r.Nc;
                    } else {
                        return external_risk_calculated;
                    }
                },

                get_CIR: function(r, obj) {
                    // get the obj of this CIR
                    // obj could be
                    // sm, lower, upper
                    if (typeof(obj)=='undefined') {
                        obj = 'sm';
                    }
                    var val = r.ae.result[this.measure].random.model[obj];

                    // calculate the CIR based on measure
                    if (this.measure == 'OR') {
                        var a = this.get_ACR(r) * val;
                        var b = 1 - this.get_ACR(r);
                        var c = a + b;
                        var d = a / c;
                        var e = d * this.baseline;
                        return d;
                    } else if (this.measure == 'RR') {
                        var a = this.get_ACR(r) * val;
                        return a;
                    }
                },

                get_ARD_old: function(r, obj) {
                    // get the obj of this CIR
                    // obj could be
                    // sm, lower, upper
                    if (typeof(obj)=='undefined') {
                        obj = 'sm';
                    }
                    var val = r.ae.result[this.measure].random.model[obj];
                    if (this.measure == 'OR') {
                        var a = (1 - val) * this.get_ACR(r);
                        var b = 1 - this.get_ACR(r);
                        var c = a + b;
                        var d = a / c;
                        var e = d * this.baseline;
                        return e;
                    } else if (this.measure == 'RR') {
                        var a = this.get_ACR(r) * (1 - val);
                        return a;
                    }
                },

                get_ARD: function(r, obj) {
                    // obj could be
                    // sm, lower, upper
                    if (typeof(obj)=='undefined') {
                        obj = 'sm';
                    }
                    var val = r.ae.result[this.measure].random.model[obj];
                    if (this.measure == 'OR') {
                        var ACR = this.get_ACR(r);
                        var CIR = this.get_CIR(r, obj);
                        var ARD = ACR - CIR;
                        return ARD;
                    } else if (this.measure == 'RR') {
                        var a = this.get_ACR(r) * (1 - val);
                        return a;
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
                    // first, find this ae in rs
                    if (this.rs.hasOwnProperty(r.ae_name)) {
                        // flip this cell!
                        this.rs[r.ae_name].is_show[cell] = 
                            !this.rs[r.ae_name].is_show[cell];
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

                show_cie_detail: function(ae_name) {
                    this.detail.cie.ae_name = ae_name;
                    tb_simple_sofpma.show_cie_detail(ae_name);
                },

                show_ctrl_options: function(ae_name) {
                    tb_simple_sofpma.show_ctrl_options(ae_name);
                }
            },
        });
    },

    toggle_ae: function(ae_name) {
        // first, find this ae in rs
        if (this.vpp.rs.hasOwnProperty(ae_name)) {
            // if exists, remove
            delete this.vpp.rs[ae_name];
        } else {
            var ae = this.data.ae_dict[ae_name];
            if (ae.stus.length == 0) {
                // this means no studies in this ae + grade 
                return;
            }
            var measure = this.vpp.measure;
        
            // build the r for display
            var r = {
                ae: ae,
                ae_name: ae.ae_name,
                ae_fullname: ae.ae_fullname,
                Et: ae.Et,
                Nt: ae.Nt,
                Ec: ae.Ec,
                Nc: ae.Nc,
                n_stu: ae.stus.length,
                which_ACR: {
                    use_internal: true,
                    use_external: false,
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

            // add this to list
            this.vpp.rs[ae_name] = r;
        }

        // have to force update the view
        tb_simple_sofpma.vpp.$forceUpdate();
    },

    clear: function() {

    },

    clear_all_ae: function() {
        for (var key in tb_simple_sofpma.vpp.rs) {
            if (tb_simple_sofpma.vpp.rs.hasOwnProperty(key)) {
                delete tb_simple_sofpma.vpp.rs[key];
            }
        }
        tb_simple_sofpma.vpp.$forceUpdate();
    },

    show_cie_detail: function(ae_name) {
        $(this.vpp_id + '_cie_detail').dialog({
            width: 400
        });
    },

    show_ctrl_options: function(ae_name) {
        $(this.vpp_id + '_ctrl_select').dialog({
            width: 300,
            my: 'left', 
            at: 'right'
        });
    }
};