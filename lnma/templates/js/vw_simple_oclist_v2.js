/*
 * Simple Outcome List
 */
var vw_simple_oclist = {
    vpp_id: '#vw_simple_oclist',
    vpp: null,
    select_mode: 'checkbox', // radio, checkbox

    sample: {
        oc_dict: {
            "fatality": {
                oc_cate: 'default',
                oc_name: 'Fatality',
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
        }
    },

    init: function(data) {
        this.data = data;

        this.oc_list = this.data.oc_list[0].oc_names.map(function(v, i) {
            return {
                oc_name: v,
                is_checked: false
            }
        });

        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                select_mode: this.select_mode,
                oc_dict: this.data.oc_dict,
                oc_list: this.oc_list
            },
            methods: {
                toggle_oc: function(oc) {
                    var oc_name = oc.oc_name;
                    oc.is_checked = !oc.is_checked;
                    // add effect
                    // if (this.select_mode == 'checkbox') {
                    //     $(event.target).toggleClass('oc-item-selected');
                    // } else {
                    //     $('.oc-item').removeClass('oc-item-selected');
                    //     $(event.target).addClass('oc-item-selected');
                    // }

                    // call the worker to update everything related
                    // jarvis will do this task accordingly
                    jarvis.toggle_oc(oc_name);
                },

                clear_all_oc: function() {
                    $('.oc-item').removeClass('oc-item-selected');
                    jarvis.clear_all_oc();
                }
            }
        });

    },

    toggle_oc: function(oc_name) {

        for (var i = 0; i < this.vpp.oc_list.length; i++) {
            var oc = this.vpp.oc_list[i];
            if (oc.oc_name == oc_name) {
                // get the oc!
                oc.is_checked = !oc.is_checked;
            }
        }
        // call the worker to update everything related
        // jarvis will do this task accordingly
        jarvis.toggle_oc(oc_name);
    }
};