var tb_ranktb = {
    box_id: '#tb_ranktb',
    vpp: null,
    vpp_id: '#tb_ranktb',
    vpp_data: {},
    
    sample: {
        header: ['Treatment', 'P-Score', 'Rank'],
        tabledata: [
            {treat: 'Ate', value: 0.91, value_rank: 1},
            {treat: 'AteBev', value: 0.89, value_rank: 2},
            {treat: 'Cabo', value: 0.87, value_rank: 3},
            {treat: 'NivoIpi', value: 0.86, value_rank: 4},
            {treat: 'PemAxi', value: 0.85, value_rank: 5},
            {treat: 'Placebo', value: 0.84, value_rank: 6},
            {treat: 'Rosi', value: 0.83, value_rank: 7},
            {treat: 'Vilda', value: 0.82, value_rank: 8},
            {treat: 'Sulfo', sucvaluera: 0.81, value_rank: 9}
        ]
    },

    col2header: {
        pscore: ['Treatment', 'P-Score', 'Rank'],
        sucra: ['Treatment', 'SUCRA', 'Rank'],
    },

    default_vpp_data: {
        header: [],
        tabledata: []
    },

    init: function() {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: this.default_vpp_data,
            methods: {

            }
        });

    },

    clear: function() {
        this.vpp.data = this.default_vpp_data;
        // hide
        $(this.box_id).hide();
    },

    draw: function(newdata, which_has_highrank) {
        if (typeof(which_has_highrank) == 'undefined') {
            which_has_highrank = 'higher';
        }
        // show
        $(this.box_id).show();

        if (newdata.rs[0].hasOwnProperty('value_rank')) {
            // which means backend has already sorted
        } else {

            
            // sort the values to get rank
            if (which_has_highrank == 'lower' ||
                which_has_highrank == 'small' ) {
                newdata.rs.sort(function(a, b) {
                    return a.value - b.value;
                });

            } else {
                newdata.rs.sort(function(a, b) {
                    return b.value - a.value;
                });
            }
            for (let i = 0; i < newdata.rs.length; i++) {
                const r = newdata.rs[i];
                newdata.rs[i]['value_rank'] = i + 1;
            }
        }
        this.vpp.header = this.col2header[newdata.col];
        this.vpp.tabledata = newdata.rs;

        this.data = newdata;
    }
}