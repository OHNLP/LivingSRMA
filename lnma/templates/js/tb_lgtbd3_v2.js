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
    r_header: 0.5,
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
        
        // init the tip
        this.tip = d3.tip()
            .attr('class', 'd3-tip')
            .direction('e')
            .offset([0,5])
            .html(function(d) {
                if (d.info == '') {
                    return null;
                }
                return d.info;
            });
        this.svg.call(this.tip);
    },
    
    clear: function() {
        this.svg.selectAll('*').remove();
        // hide
        $(this.box_id).hide();
    },

    /**
     * Convert this.data to D3.js data format (list)
     */
    conv_table2list: function() {
        this.datalist = [];
        for (let i = 0; i < this.data.n; i++) {
            var row = this.data.cols[i];
            for (let j = 0; j < this.data.n; j++) {
                var col = this.data.cols[j];
                var val = this.data.tabledata[i].stat[j];
                var lci = this.data.tabledata[i].lci[j];
                var uci = this.data.tabledata[i].uci[j];

                var info = '';
                if (i != j) {
                    info = '<table>' +
                            '<tr>' +
                                '<td colspan="2"><b>'+col+'</b> vs <b>'+row+'</b></td>' +
                            '</tr>' +
                            '<tr>' +
                                '<td>Effect: </td>' +
                                '<td>'+val.toFixed(2)+'</td>' +
                            '</tr>' +
                            '<tr>' +
                                '<td>95% CI: </td>' +
                                '<td>('+lci.toFixed(2)+', '+uci.toFixed(2)+')</td>' +
                            '</tr>' +
                        '</table>';                    
                }
                
                this.datalist.push({
                    i: i,
                    j: j,
                    row: row,
                    col: col,
                    val: val,
                    lci: lci,
                    uci: uci,
                    info: info
                });
            }
        }
    },

    draw: function(data) {
        // bind and transform data
        this.data = data;
        this.conv_table2list();

        // show this box
        $(this.box_id).show();

        // update the width and height of svg
        // + 1 is for the top+left header
        // + 0.5 is for the header name
        this.width = (data.n + 1 + 0.5) * this.width_cell;
        this.height = (data.n + 1 + 0.5) * this.height_cell;
        this.svg.attr('width', this.width)
            .attr('height', this.height);
        // update the box width
        $(this.box_id).css('width', this.width);

        // get the values
        this._draw_header();

        // draw table
        var cells = this.svg.selectAll('g.cell')
            .data(this.datalist)
            .enter()
            .append('g')
            .attr('class', function(d, i) {
                if (d.i == d.j) {
                    return 'ctc';
                } else {
                    return 'cell';
                }
            })
            .attr('transform', function(d, i) {
                var cell_x = (tb_lgtbd3.r_header + 1 + d.j) * tb_lgtbd3.width_cell;
                var cell_y = (tb_lgtbd3.r_header * 2 + d.i) * tb_lgtbd3.height_cell;
                return 'translate('+cell_x+', '+cell_y+')'
            })
            .on('mouseover', this.tip.show)
            .on('mouseout', this.tip.hide);
            
        // unbind hover event of ctc
        this.svg.selectAll('g.ctc')
            .on('mouseover', null)
            .on('mouseout', null);

        // draw the cell background
        cells.append('rect')
            .attr('width', this.width_cell)
            .attr('height', this.height_cell)
            .attr('fill', function(d, i) {
                if (d.i == d.j) {
                    return tb_lgtbd3.color_ctc;
                } else {
                    return tb_lgtbd3.color_scale2(d.val, d.lci, d.uci);
                }
            })
            .attr('stroke', this.color_border);

        // draw the cell text
        var t_vals = cells.append('text')
            .attr('x', this.width_cell / 2)
            .attr('y', this.height_cell / 2)
            .attr('font-size', this.font_size)
            .attr('alignment-baseline', 'middle')
            .attr('text-anchor', 'middle');
        t_vals.append('tspan')
            .attr('x', this.width_cell / 2)
            .attr('y', this.height_cell / 2)
            .text(function(d, i) {
                if (d.i == d.j) {
                    return '';
                } else {
                    return d.val.toFixed(2);
                }
            });
        t_vals.append('tspan')
            .attr('x', this.width_cell / 2)
            .attr('y', this.height_cell / 2 + this.font_size)
            .text(function(d, i) { 
                if (d.i == d.j) {
                    return '';
                } else {
                    return '('+d.lci.toFixed(2)+', '+d.uci.toFixed(2)+')';
                }
            });
    },


    _draw_header: function() {
        var tmp_x = (this.r_header + 1 + this.data.n / 2) * this.width_cell;
        var tmp_y = (this.r_header * 0.5) * this.height_cell;
        var g_header = this.svg.append("g")
            .attr('class', 'header');
        g_header.append('text')
            .attr('x', tmp_x)
            .attr('y', tmp_y)
            .attr('font-size', this.font_size)
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'middle')
            .text('Treatments');
        g_header.append('line')
            .attr('x1', (this.r_header + 1) * this.width_cell)
            .attr('x2', (this.r_header + 1 + this.data.n) * this.width_cell)
            .attr('y1', (this.r_header) * this.height_cell)
            .attr('y2', (this.r_header) * this.height_cell)
            .attr('stroke', this.color_ctc);

        // draw the header column
        tmp_x = (this.r_header * 0.6) * this.width_cell;
        tmp_y = (this.r_header * 2 + this.data.n / 2) * this.height_cell;
        g_header.append('text')
            .attr('x', tmp_x)
            .attr('y', tmp_y)
            .attr('font-size', this.font_size)
            .attr('text-anchor', 'middle')
            .attr('transform', 'rotate(-90, '+tmp_x+', '+tmp_y+')')
            .text('Comparator');
        g_header.append('line')
            .attr('x1', (this.r_header) * this.width_cell)
            .attr('x2', (this.r_header) * this.width_cell)
            .attr('y1', (this.r_header * 2) * this.height_cell)
            .attr('y2', (this.r_header * 2 + this.data.n) * this.height_cell)
            .attr('stroke', this.color_ctc);

        // the the header texts of treatment
        for (let i = 0; i < this.data.n; i++) {
            var header = this.data.cols[i];
            // in each col, 0.5 is the line middle
            tmp_x = (this.r_header + 1 + i + 0.5) * this.width_cell;
            tmp_y = (this.r_header * 1.5) * this.height_cell;
            g_header.append('text')
                .attr('x', tmp_x)
                .attr('y', tmp_y)
                .attr('font-size', this.font_size)
                .attr('text-anchor', 'middle')
                .attr('alignment-baseline', 'middle')
                .text(header);

            // in each row, this.font_size / 2 is similar to 0.5em
            tmp_x = this.r_header * this.width_cell + this.font_size / 2;
            tmp_y = (this.r_header * 2 + i + 0.5) * this.height_cell;
            g_header.append('text')
                .attr('x', tmp_x)
                .attr('y', tmp_y)
                .attr('font-size', this.font_size)
                .attr('text-anchor', 'start')
                .attr('alignment-baseline', 'middle')
                .text(header);
        }
    },

    draw2: function(data) {
        this.data = data;
        // show
        $(this.box_id).show();

        // update the width and height of svg
        // + 1 is for the top+left header
        // + 0.5 is for the header name
        this.width = (data.n + 1 + 0.5) * this.width_cell;
        this.height = (data.n + 1 + 0.5) * this.height_cell;
        this.svg.attr('width', this.width)
            .attr('height', this.height);

        // remove all old nodes and links
        // this.svg.selectAll("*").remove();
        
        // draw the header name
        this._draw_header();
        
        // draw the table body
        for (let i = 0; i < this.data.n; i++) {
            var row = this.data.cols[i];

            for (let j = 0; j < this.data.n; j++) {
                var col = this.data.cols[j];
                var val = this.data.tabledata[i].stat[j];
                var lci = this.data.tabledata[i].lci[j];
                var uci = this.data.tabledata[i].uci[j];
                // console.log('* add row ' + row + ' col ' + col);

                // draw a cell here
                var cell_x = (this.r_header + 1 + j) * this.width_cell;
                var cell_y = (this.r_header * 2 + i) * this.height_cell;
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
                    // g_cell.append('text')
                    //     .attr('x', this.width_cell / 2)
                    //     .attr('y', this.height_cell / 2)
                    //     .attr('text-anchor', 'middle')
                    //     .attr('alignment-baseline', 'middle')
                    //     .attr('font-size', this.font_size * 1.1)
                    //     .attr('font-weight', 'bold')
                    //     .text(row);
                    continue
                }

                // the val and others
                g_cell.append('rect')
                    .attr('width', this.width_cell)
                    .attr('height', this.height_cell)
                    .attr('fill', this.color_scale2(val, lci, uci))
                    .attr('stroke', this.color_border)
                    .on('mouseover', this.tip.show) // bind hover event
                    .on('mouseout', this.tip.hide);

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