var tb_lgtbd3 = {
    box_id: '#tb-nma-league',
    plot_id: '#tb_lgtbd3',
    plot_type: 'd3js',
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

    // for d3.js
    svg: null,
    width: 500,
    height: 400,
    width_cell: 72,
    height_cell: 32,
    font_size: 12,
    color_ctc: '#DFDFDF',
    color_border: 'whitesmoke',
    color_scale: d3.scaleLinear()
        .domain([0, 1, 3])
        .range(['#78b787', 'white', '#ff0000']),
    color_scale_range: [0, 0.9, 1, 1.1, 2],
    color_scale2: function(hr, lower, upper) {
        // there are 4 cases:
        if (hr > 1) {
            if (lower > 1 && upper > 1) {
                return this.color_scale(hr>this.color_scale_range[3]?hr:this.color_scale_range[3]);
            } else {
                return this.color_scale(this.color_scale_range[3]);
            }

        } else if (hr < 1) {
            if (lower < 1 && upper < 1) {
                return this.color_scale(hr<this.color_scale_range[1]?hr:this.color_scale_range[1]);
            } else {
                return this.color_scale(this.color_scale_range[1]);
            }
        } else {
            return this.color_scale(this.color_scale_range[2])
        }
    },

    init: function() {
        this.svg = d3.select(this.plot_id)
            .attr('width', this.width)
            .attr('height', this.height);
    },
    
    clear: function() {
        this.svg.selectAll('*').remove();
        // hide
        $(this.box_id).hide();
    }, 

    draw: function(data) {
        this.data = data;
        // show
        $(this.box_id).show();

        // update the width and height of svg
        this.width = data.n * this.width_cell;
        this.height = data.n * this.height_cell;
        this.svg.attr('width', this.width)
            .attr('height', this.height);

        // remove all old nodes and links
        // this.svg.selectAll("*").remove();

        for (let i = 0; i < this.data.n; i++) {
            var row = this.data.cols[i];
            for (let j = 0; j < this.data.n; j++) {
                var col = this.data.cols[j];
                var val = this.data.tabledata[i].stat[j];
                var lci = this.data.tabledata[i].lci[j];
                var uci = this.data.tabledata[i].uci[j];
                // console.log('* add row ' + row + ' col ' + col);

                // draw a cell here
                var cell_x = j * this.width_cell;
                var cell_y = i * this.height_cell;
                var g_cell = this.svg.append('g')
                    .attr('class', 'cell')
                    .attr('transform', 'translate('+cell_x+', '+cell_y+')');

                // draw a cell background rect
                
                // the text if ctc?
                if (row == col) {
                    g_cell.append('rect')
                        .attr('width', this.width_cell)
                        .attr('height', this.height_cell)
                        .attr('fill', this.color_ctc)
                        .attr('stroke', this.color_border);
                    g_cell.append('text')
                        .attr('x', this.width_cell / 2)
                        .attr('y', this.height_cell / 2)
                        .attr('text-anchor', 'middle')
                        .attr('alignment-baseline', 'middle')
                        .attr('font-size', this.font_size * 1.1)
                        .attr('font-weight', 'bold')
                        .text(row);
                    continue
                }

                // the val and others
                g_cell.append('rect')
                    .attr('width', this.width_cell)
                    .attr('height', this.height_cell)
                    .attr('fill', this.color_scale2(val, lci, uci))
                    .attr('stroke', this.color_border);
                var t_vals = g_cell.append('text')
                    .attr('x', this.width_cell / 2)
                    .attr('y', this.height_cell / 2)
                    .attr('font-size', this.font_size)
                    .attr('alignment-baseline', 'middle')
                    .attr('text-anchor', 'middle');
                t_vals.append('tspan')
                    .attr('x', this.width_cell / 2)
                    .attr('y', this.height_cell / 2)
                    .text(val.toFixed(2));
                t_vals.append('tspan')
                    .attr('x', this.width_cell / 2)
                    .attr('y', this.height_cell / 2 + this.font_size)
                    .text('('+lci.toFixed(2)+', '+uci.toFixed(2)+')');
                
            }
        }
    }
};