/*
 * SoF Table PMA
 */
var tb_sofpma = {
    vpp: null,
    vpp_id: '#tb_sofpma',
    sample: {
        measure: 'OR',
        baseline: 1000,
        external_risk_calculated: 10,
        use_internal_baseline: true,
        rs: {
            GA: {},
            G3H: {},
            G5N: {}
        }
    },

    init: function(data) {
        this.data = data;

        this.vpp = new Vue({
            el: this.vpp_id,
            data: this.sample,
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

                flip_cell: function(ae_grade, r, cell) {
                    // first, find this ae in rs
                    if (this.rs[ae_grade].hasOwnProperty(r.name)) {
                        // flip this cell!
                        this.rs[ae_grade][r.name].is_show[cell] = 
                            !this.rs[ae_grade][r.name].is_show[cell];
                    } else {
                        // how can it be ???
                    }
                    this.$forceUpdate();
                }
            },
        });
    },

    toggle_ae: function(ae_cate, ae_name, ae_grade) {
        // first, find this ae in rs
        if (this.vpp.rs[ae_grade].hasOwnProperty(ae_name)) {
            // if exists, remove
            delete this.vpp.rs[ae_grade][ae_name];
        } else {
            var ae = this.data.ae_rsts[ae_name][ae_grade];
            if (ae.stus.length == 0) {
                // this means no studies in this ae + grade 
                return;
            }
            var measure = this.vpp.measure;
        
            // build the r for display
            var r = {
                name: ae_name,
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
            this.vpp.rs[ae_grade][ae_name] = r;
        }

        // have to force update the view
        tb_sofpma.vpp.$forceUpdate();
    },

    clear: function() {

    },

    clear_all: function() {
        for (var key in tb_sofpma.vpp.rs) {
            if (tb_sofpma.vpp.rs.hasOwnProperty(key)) {
                tb_sofpma.vpp.rs[key] = {};
            }
        }
        tb_sofpma.vpp.$forceUpdate();
    }
};