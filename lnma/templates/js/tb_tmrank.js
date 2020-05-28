var tb_tmrank = {
    box: null,
    box_id: '#tb-nma-ranks',
    vpp: null,
    vpp_id: '#tb-nma-ranks',
    data: {},
    width: 400,
    
    sample: {
        tabledata: [
            {treat: 'Ate', sucra: 0.91, sucra_rank: 1, pscore: 0.45, pscore_rank: 0.23},
            {treat: 'AteBev', sucra: 0.89, sucra_rank: 2, pscore: 0.45, pscore_rank: 0.23},
            {treat: 'Cabo', sucra: 0.87, sucra_rank: 3, pscore: 0.45, pscore_rank: 0.23},
            {treat: 'NivoIpi', sucra: 0.86, sucra_rank: 4, pscore: 0.45, pscore_rank: 0.23},
            {treat: 'PemAxi', sucra: 0.85, sucra_rank: 5, pscore: 0.45, pscore_rank: 0.23},
            {treat: 'Placebo', sucra: 0.84, sucra_rank: 6, pscore: 0.45, pscore_rank: 0.23},
            {treat: 'Rosi', sucra: 0.83, sucra_rank: 7, pscore: 0.45, pscore_rank: 0.23},
            {treat: 'Vilda', sucra: 0.82, sucra_rank: 8, pscore: 0.45, pscore_rank: 0.23},
            {treat: 'Sulfo', sucra: 0.81, sucra_rank: 9, pscore: 0.45, pscore_rank: 0.23}
        ]
    },

    sample2: {
        col: 'sucra',
        rs: [
            {treat: 'Suni', value: 98},
            {treat: 'Ate', value: 88},
            {treat: 'Rosi', value: 82}
        ]
    },
    
    init: function() {
        this.box = $(this.box_id)
            .css('width', this.width);

        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                n: 0,
                tabledata: []
            },
            methods: {
                update_table: function(data) {
                    this.tabledata = data;
                }
            }
        });
    },

    clear: function() {
        this.vpp.n = 0;
        this.vpp.tabledata = [];
        this.data = {};
    },

    draw: function(data) {
        this.vpp.update_table(data);
    },

    draw_col: function(newdata) {
        // sort the newdata rs
        newdata.rs.sort(function(a, b) {
            return b.value - a.value;
        })
        for (let i = 0; i < newdata.rs.length; i++) {
            const r = newdata.rs[i];
            const treat = r.treat;
            const value = r.value;
            if (!this.data.hasOwnProperty(treat)) {
                this.data[treat] = {
                    'treat': treat
                };
            }
            this.data[treat][newdata.col] = value;
            // also, update the rank of this col
            var rank_val = i + 1;
            this.data[treat][newdata.col + '_rank'] = rank_val;
        }
        this.draw(Object.values(this.data));
    }
}