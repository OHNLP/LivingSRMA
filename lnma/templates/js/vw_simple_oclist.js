/*
 * Simple Outcome List
 */
var vw_simple_oclist = {
    vpp_id: '#vw_simple_oclist',
    vpp: null,
    select_mode: 'checkbox', // radio, checkbox

    sample: {
        ae_dict: {
            "fatality": {
                ae_cate: 'default',
                ae_name: 'Fatality',
                treat_list: ['Suni', 'Pazo', 'Ipin', 'ApiX'],
                treats: {
                    "Suni": { event: 110, total: 200, rank: 1},
                    "Ipin": { event: 111, total: 220, rank: 2},
                    "Pazo": { event: 112, total: 250, rank: 3},
                    "ApiX": { event: 113, total: 270, rank: 4}
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
            "major-bleeding": {
                ae_cate: 'default',
                ae_name: 'Major bleeding',
                treat_list: ['Suni', 'Pazo', 'Ipin', 'ApiX'],
                treats: {
                    "Suni": { event: 10, total: 200, rank: 1},
                    "Ipin": { event: 11, total: 220, rank: 2},
                    "Pazo": { event: 12, total: 250, rank: 3},
                    "ApiX": { event: 13, total: 270, rank: 4}
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

        this.ae_list = this.data.ae_list[0].ae_names.map(function(v, i) {
            return {
                ae_name: v,
                is_checked: false
            }
        });

        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                select_mode: this.select_mode,
                ae_dict: this.data.ae_dict,
                ae_list: this.ae_list
            },
            methods: {
                toggle_ae: function(ae) {
                    var ae_name = ae.ae_name;
                    ae.is_checked = !ae.is_checked;
                    // add effect
                    // if (this.select_mode == 'checkbox') {
                    //     $(event.target).toggleClass('ae-item-selected');
                    // } else {
                    //     $('.ae-item').removeClass('ae-item-selected');
                    //     $(event.target).addClass('ae-item-selected');
                    // }

                    // call the worker to update everything related
                    // jarvis will do this task accordingly
                    jarvis.toggle_ae(ae_name);
                },

                clear_all_ae: function() {
                    $('.ae-item').removeClass('ae-item-selected');
                    jarvis.clear_all_ae();
                }
            }
        });

    },

    toggle_ae: function(ae_name) {

        for (var i = 0; i < this.vpp.ae_list.length; i++) {
            var ae = this.vpp.ae_list[i];
            if (ae.ae_name == ae_name) {
                // get the AE!
                ae.is_checked = !ae.is_checked;
            }
        }
        // call the worker to update everything related
        // jarvis will do this task accordingly
        jarvis.toggle_ae(ae_name);
    }
};