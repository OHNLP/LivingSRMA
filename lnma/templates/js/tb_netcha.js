var tb_netcha = {
    vpp: null,
    vpp_id: '#tb-nma-netcha',
    data: null,
    sample: {
        tabledata: [
            { "cha": "# Interventions", "val": 8 },
            { "cha": "# Studies", "val": 28 },
            { "cha": "# Patients in Network", "val": 146528 },
            { "cha": "# Possible Pairwise Comparisons", "val": 28 },
            { "cha": "# Direct Pairwise Comparisons", "val": 13 },
            { "cha": "Is the network connected?", "val": true },
            { "cha": "# Two-arm Studies", "val": 26 },
            { "cha": "# Multi-Arms Studies", "val": 2 },
            { "cha": "# Events in Network", "val": 12009 },
            { "cha": "# Studies With No Zero Events", "val": 28 },
            { "cha": "# Studies With At Least One Zero Event", "val": 0 },
            { "cha": "# Studies with All Zero Events", "val": 0 }
        ]
    },

    init: function() {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                tabledata: []
            },

            methods: {
                update_table: function(tabledata) {
                    this.tabledata = tabledata;
                }
            }
        })
    },

    clear: function() {
        this.vpp.tabledata = [];
    },

    draw: function(data) {
        this.data = data;
        this.vpp.update_table(data);
    }
}