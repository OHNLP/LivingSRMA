/*
 * SoF Table PMA
 */
var tb_simple_sofpma = {
    vpp: null,
    vpp_id: '#tb_simple_sofpma',

    init: function(data) {
        this.data = data;

        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                measure: 'OR',
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
                        return r.Ec / r.Nc * this.baseline;
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

                    // calculate the CIR based on measure
                    if (this.measure == 'OR') {
                        var a = this.get_ACR(r) / this.baseline * r[obj];
                        var b = 1 - this.get_ACR(r) / this.baseline;
                        var c = a + b;
                        var d = a / c;
                        var e = d * this.baseline;
                        return e;
                    } else if (this.measure == 'RR') {
                        var a = this.get_ACR(r) * r[obj];
                        return a;
                    }
                },

                get_ARD: function(r, obj) {
                    // get the obj of this CIR
                    // obj could be
                    // sm, lower, upper
                    if (typeof(obj)=='undefined') {
                        obj = 'sm';
                    }
                    if (this.measure == 'OR') {
                        var a = (1 - r[obj]) * this.get_ACR(r) / this.baseline;
                        var b = 1 - this.get_ACR(r) / this.baseline;
                        var c = a + b;
                        var d = a / c;
                        var e = d * this.baseline;
                        return e;
                    } else if (this.measure == 'RR') {
                        var a = this.get_ACR(r) * (1 - r[obj]);
                        return a;
                    }
                },

                get_ARD_txt: function(r, obj) {
                    var ARD = this.get_ARD(r, obj);
                    var txt = ' less';
                    if (ARD < 0) {
                        txt = ' more';
                    }
                    return Math.abs(ARD).toFixed(0) + txt;
                },

                get_ARDp_txt: function(r, obj) {
                    var ARDp = 100 * this.get_ARD(r, obj) / this.baseline;
                    var txt = ' less';
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
                sm: ae.result[measure].random.model.sm,
                lower: ae.result[measure].random.model.lower,
                upper: ae.result[measure].random.model.upper,
                Et: ae.Et,
                Nt: ae.Nt,
                Ec: ae.Ec,
                Nc: ae.Nc,
                n_stu: ae.stus.length,
                // for display setting
                is_show: {
                    // show sm / study info
                    sm: true,
                    // show ARD / ARD CI
                    ARD: true
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
    }
};