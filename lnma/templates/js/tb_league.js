var tb_league = {
    box: null,
    box_id: '#tb-nma-league',
    vpp: null,
    vpp_id: '#tb-nma-league',
    data: null,
    width: 300,
    width_row_name: 80,
    width_cell: 72,
    min_bg_color: '#78b787',
    mid_bg_color: 'white',
    max_bg_color: '#ff0000',
    ctc_bg_color: 'lightgrey',
    sample: {
        n: 4,
        cols: ['pazo', 'ni-ip', 'ate-bev', 'cabo'],
        tabledata: [
            {row: 'pazo', stat: [1, 1.19, 1.23, 1.53], 
                lci: [1, 0.89, 0.91, 1.09], uci: [1, 1.59, 1.66, 2.13], star: ['', '', '**', '']},
            {row: 'ni-ip', stat: [0.84, 1, 1.03, 1.29], 
                lci: [0.63, 1, 0.87, 1.09], uci: [1.59, 1, 2.13, 1.61], star: ['', '', '', '**']},
            {row: 'ate-bev', stat: [0.82, 1.19, 1, 1.53], 
                lci: [1, 0.89, 0.91, 1.09], uci: [1, 1.59, 1.66, 2.13], star: ['', '', '', '']},
            {row: 'cabo', stat: [0.65, 1.19, 1.23, 1], 
                lci: [1, 0.89, 0.91, 1.09], uci: [1, 1.59, 1.66, 2.13], star: ['**', '**', '', '']},
        ],
        fig_fn: '',
        backend: 'bugsnet',
        min_max: [-1, 1]
    },

    league_table_explains: {
        'netmeta2': '<p>Estimated HR (with 95% Confidence Interval) reflect outcomes for treatment in columns compared to treatment in rows.</p>',
        'netmeta': '<p>Estimated HR (with 95% Confidence Interval) reflect outcomes for treatment in columns compared to treatment in rows.</p>',
        'bugsnet': '<p>The values in each cell represent the relative treatment effect (and 95% credible intervals) of the treatment on the top, compared to the treatment on the left.</p>'
    },
    
    init: function() {
        this.box = $(this.box_id)
            .css('width', this.width);

        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                n: 0,
                cols: [],
                tabledata: [],
                fig_fn: '',
                league_table_explain: '',
                backend: ''
            },
            methods: {
                update_table: function(data) {
                    this.backend = data.backend;
                    this.n = data.n;
                    this.cols = data.cols;
                    this.tabledata = data.tabledata;
                    this.fig_fn = data.fig_fn;
                    this.league_table_explain = tb_league.league_table_explains[data.backend];
                },

                fmt_val: function(v) {
                    if (typeof(v) == 'number') {
                        return v.toFixed(2);
                    } else if (typeof(v) == 'string') { 
                        return v;
                    } else {
                        return v;
                    }
                },

                get_bg_color: function(v, row, col) {
                    if (row == col) {
                        return tb_league.ctc_bg_color;
                    } else {
                        return tb_league.cell_bg_color_scale(v);
                    }
                }
            },
            updated: function() {
                // $('.tb-cell').css('background-color', '');
                // $('.row-'+fm_config.get_config().treat).css('background-color', 'lightblue');
                // $('.col-'+fm_config.get_config().treat).css('background-color', 'mistyrose');
            }
        });
    },

    clear: function() {
        this.draw({
            n: 5,
            cols: [],
            tabledata: [],
            fig_fn: '',
            league_table_explain: '',
            min_max: [-1, 1]
        })
    },

    draw: function(data) {
        this.data = data;

        // the width of league table is decided by the number columns
        this.width = this.width_cell * data.n + 8;
        if (data.backend === 'bugsnet') {
            this.width += 115;
        }
        // this.width = this.width_row_name + this.width_cell * data.n + 8;
        this.box = $(this.box_id)
            .css('width', this.width);

        // update the color scale
        this.cell_bg_color_scale = d3.scaleLinear()
            .domain([
                data.min_max[0],
                1,
                data.min_max[1],
            ])
            .range([
                d3.rgb(this.min_bg_color), 
                d3.rgb(this.mid_bg_color),
                d3.rgb(this.max_bg_color)
            ]);

        this.vpp.update_table(data);
    }
}