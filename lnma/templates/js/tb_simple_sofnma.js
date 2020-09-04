/*
 * Sof Table NMA
 */

var tb_simple_sofnma = {
    vpp: null,
    vpp_id: '#tb_simple_sofnma',
    default_comparator: null,
    color_scale: d3.scaleLinear()
        .domain([0, 1, 3])
        .range(['#78b787', 'white', '#ff0000']),

    sample: {
        measure: 'OR',
        baseline: 1000,
        external_risk_calculated: 10,
        use_internal_baseline: true,
        comparator: 'Suni',
        treat_list: ['Suni', 'Pazo', 'Ipin', 'ApiX'],
        ae_dict: {
            "fatality": {
                ae_cate: 'default',
                ae_name: 'Fatality',
                treat_list: ['Suni', 'Pazo', 'Ipin', 'ApiX'],
                treats: {
                    "Suni": { event: 110, total: 200, rank: 1, n_stus: 1 },
                    "Ipin": { event: 111, total: 220, rank: 2, n_stus: 1 },
                    "Pazo": { event: 112, total: 250, rank: 3, n_stus: 1 },
                    "ApiX": { event: 113, total: 270, rank: 4, n_stus: 1 }
                },
                // for each one, row is comparator, col is 
                lgtable: {
                    OR: {
                        Suni: {
                            "Suni": {}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "Pazo": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "Ipin": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "ApiX": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {}
                        }
                    },
                    RR: {
                        "Suni": {
                            "Suni": {}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "Pazo": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "Ipin": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "ApiX": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {}
                        }
                    }
                }
            },
            "major-bleeding": {
                ae_cate: 'default',
                ae_name: 'Major bleeding',
                treat_list: ['Suni', 'Pazo', 'Ipin', 'ApiX'],
                treats: {
                    "Suni": { event: 110, total: 200, rank: 1, n_stus: 1 },
                    "Ipin": { event: 111, total: 220, rank: 2, n_stus: 1 },
                    "Pazo": { event: 112, total: 250, rank: 3, n_stus: 1 },
                    "ApiX": { event: 113, total: 270, rank: 4, n_stus: 1 }
                },
                // for each one, row is comparator, col is 
                lgtable: {
                    OR: {
                        "Suni": {
                            "Suni": {}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "Pazo": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "Ipin": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "ApiX": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {}
                        },
                    },
                    RR: {
                        "Suni": {
                            "Suni": {}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "Pazo": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "Ipin": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {}, "ApiX": {sm: 1.1, lw: 0.4, up: 1.2}
                        },
                        "ApiX": {
                            "Suni": {sm: 1.1, lw: 0.4, up: 1.2}, "Pazo": {sm: 1.1, lw: 0.4, up: 1.2}, "Ipin": {sm: 1.1, lw: 0.4, up: 1.2}, "ApiX": {}
                        },
                    }
                }
            },
        }
    },

    init: function(data) {
        this.data = data;

        // get all treats
        var default_ae_name = data.ae_list[0]['ae_names'][0];
        var treat_list = data.ae_dict[default_ae_name]['treat_list'];
        if (this.default_comparator == null || this.default_comparator == '') {
            this.default_comparator = treat_list[0];
        }
        var default_treat = treat_list[1];

        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                measure: 'OR',
                baseline: 1000,
                external_risk_calculated: 10,
                use_internal_baseline: true,
                detail: {
                    ae_name: default_ae_name,
                    treat: default_treat
                },

                comparator: this.default_comparator,
                treat_list: treat_list,
                ae_dict: this.data.ae_dict,
                rs: {}
            },
            methods: {
                get_ACR: function(r) {
                    if (this.use_internal_baseline) {
                        return r.event / r.total;
                    } else {
                        return external_risk_calculated;
                    }
                },

                get_CIR: function(r, v) {
                    // get the obj of this CIR
                    // v could be OR/RR's
                    // sm, lower, upper
                    // calculate the CIR based on measure
                    if (this.measure == 'OR') {
                        var a = this.get_ACR(r) * v;
                        var b = 1 - this.get_ACR(r);
                        var c = a + b;
                        var d = a / c;
                        var e = d * this.baseline;
                        return d;
                    } else if (this.measure == 'RR') {
                        var a = this.get_ACR(r) * v;
                        return a;
                    }
                },

                show_sm: function(tb, c, t) {
                    console.log(tb);
                    return tb[c][t].sm;
                },

                get_ARD: function(r, v) {
                    // get the ARD of this CIR
                    // v could be OR/RR's
                    // sm, lower, upper
                    if (this.measure == 'OR') {
                        var ACR = this.get_ACR(r);
                        var CIR = this.get_CIR(r, v);
                        var ARD = ACR - CIR;
                        return ARD;
                    } else if (this.measure == 'RR') {
                        var a = this.get_ACR(r) * (1 - v);
                        return a;
                    }
                },

                get_ARD_txt: function(r, v) {
                    var ARD = this.get_ARD(r, v);
                    var txt = ' fewer';
                    if (ARD < 0) {
                        txt = ' more';
                    }
                    return Math.abs(Math.round(ARD * this.baseline)) + txt;
                },

                get_ARDp: function(r, v) {
                    var ARDp = 100 * this.get_ARD(r, v);
                    return Math.abs(ARDp).toFixed(1) + '%';
                },

                get_ARDp_txt: function(r, v) {
                    var ARDp = 100 * this.get_ARD(r, v);
                    var txt = ' fewer';
                    if (ARDp < 0) {
                        txt = ' more';
                    }
                    return Math.abs(ARDp).toFixed(1) + '%' + txt;
                },

                get_grade_label: function(g) {
                    return jarvis.texts[g];
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

                show_detail: function(ae_name, treat) {
                    this.detail.ae_name = ae_name;
                    this.detail.treat = treat;

                    tb_simple_sofnma.show_detail(ae_name, treat, this.comparator);
                },

                txt: function(t) {
                    return jarvis.txt[t];
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
            // add this to list
            this.vpp.rs[ae_name] = ae;
        }

        // have to force update the view
        tb_simple_sofnma.vpp.$forceUpdate();
    },

    show_detail: function(ae_name, treat, comparator) {
        $(this.vpp_id + '_detail').dialog({
            width: 600
        });
    },

    clear: function() {

    },

    clear_all_ae: function() {
        for (var key in tb_simple_sofnma.vpp.rs) {
            if (tb_simple_sofnma.vpp.rs.hasOwnProperty(key)) {
                delete tb_simple_sofnma.vpp.rs[key];
            }
        }
        tb_simple_sofnma.vpp.$forceUpdate();
    }
};