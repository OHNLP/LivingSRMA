var fg_prim_forest = {
    box_id: '#fg_prim_forest',
    plot_id: '#fg_prim_forest_svg',
    plot_type: 'd3js',
    svg: null,
    cols: [
        {width: 120, align: 'start',  name: 'Study', x: 0, row: 2},
        {width: 50,  align: 'end',    name: 'Events', row: 2},
        {width: 50,  align: 'end',    name: 'Total', row: 2},
        {width: 50,  align: 'end',    name: 'Events', row: 2},
        {width: 50,  align: 'end',    name: 'Total', row: 2},
        {width: 50,  align: 'end',    name: '$SM$', row: 2},
        {width: 100, align: 'end',    name: '95% CI', row: 2},
        {width: 200, align: 'middle', name: '$SM_NAME$ (95% CI)', row: 2},
        {width: 100, align: 'end',    name: 'Relative weight', row: 2}
    ],
    row_height: 15,
    min_dot_size: 4,
    row_txtmb: 3,
    row_frstml: 20,
    default_height: 300,

    css: {
        txt_bd: 'prim-frst-txt-bd',
        txt_nm: 'prim-frst-txt-nm',
        txt_mt: 'prim-frst-txt-mt',
        txt_sm: 'prim-frst-txt-sm',
        txt_clickable: 'prim-frst-txt-clickable',
        stu_g: 'prim-frst-stu-g',
        stu_bg: 'prim-frst-stu-bg',
        stu_rect: 'prim-frst-stu-rect'
    },
    css_html: ["<style>",
        ".prim-frst-txt-bd{ font-weight: bold; }",
        ".prim-frst-txt-nm{ font-weight: normal; }",
        ".prim-frst-txt-mt{ font-family: Times; font-style: italic; }",
        ".prim-frst-txt-sm{ font-size: xx-small; }",
        ".prim-frst-stu-g text{ cursor: default; }",
        ".prim-frst-stu-bg{ fill: white; }",
        ".prim-frst-stu-rect{ fill: black; }",
        ".prim-frst-stu-line{ stroke: black; stroke-width: 1.5; }",
        ".prim-frst-stu-model{ fill: red; stroke: black; stroke-width: 1; }",
        ".prim-frst-stu-model-refline{ stroke: black; stroke-width: 1; }",
        ".prim-frst-stu-g:hover .prim-frst-stu-bg{ fill: whitesmoke; }",
        ".prim-frst-txt-clickable{ fill: #00397b; cursor: pointer !important; }",
        ".prim-frst-txt-clickable:hover{ fill: blue; }",
        "</style>"
    ].join('\n'),

    _x_scale: function(v) {
        var x = this.x_scale(v);

        if (x.toString() == 'NaN') {
            return 0;
        } else {
            if (x < 0) {
                return 0;
            }
            return x;
        }
    },

    init: function() {
        // add CSS classes
        $(this.box_id).append(this.css_html);

        // set the width of this plot
        this.width = 0;
        for (var i = 0; i < this.cols.length; i++) {
            var col = this.cols[i];
            col.x = i>0? this.cols[i-1].x + this.cols[i-1].width : 0;
            this.width += col.width;
        }
        
        // set the default height this plot
        this.height = this.default_height;

        // init the svg
        this.svg = d3.select(this.plot_id)
            .attr('width', this.width)
            .attr('height', this.height);
    },

    draw: function(data, cfg) {
        // clear the old plot first
        this.clear();

        // bind new data
        this.data = data;
        this.cfg = cfg;

        // update the height of svg according to number of studies
        // 8 is the number of lines of header and footers
        this.height = this.row_height * (this.data.stus.length + 8);
        this.svg.attr('height', this.height);

        // show header
        this._draw_header();
        
        // show studies
        this._draw_study_vals();
        
        // show the model text
        this._draw_heter();

        // show the plot
        this._draw_forest();

    },

    _draw_header: function() {
        this.svg.append('text')
            .attr('class', this.css.txt_bd)
            .attr('x', this.cols[3].x)
            .attr('y', this.row_height)
            .attr('text-anchor', "end")
            .text('Treatment');
        
        this.svg.append('text')
            .attr('class', this.css.txt_bd)
            .attr('x', this.cols[5].x)
            .attr('y', this.row_height)
            .attr('text-anchor', "end")
            .text('Control');
        
        for (var i = 0; i < this.cols.length; i++) {
            var col = this.cols[i];
            var x = col.x + (col.align=='start'? 0 : col.align=='end'? col.width : col.width / 2);
            this.svg.append('text')
                .attr('class', this.css.txt_bd)
                .attr('x', x)
                .attr('y', this.row_height * col.row)
                .attr('text-anchor', col.align)
                .text(this._conv_col_name(col.name));
        }
    },

    _conv_col_name: function(name) {
        var ret = name;
        ret = ret.replace(/\$SM_NAME\$/g, this.cfg.sm.name);
        ret = ret.replace(/\$SM\$/g, this.cfg.sm.sm);
        return ret;
    },

    _draw_study_vals: function() {
        // the studies
        for (var i = 0; i < this.data.stus.length; i++) {
            var stu = this.data.stus[i];
            var g = this.svg.append('g')
                .attr('class', this.css.stu_g)
                .attr('transform', 'translate(0, ' + (this.row_height * (3 + i)) + ')');

            // add a background for display
            g.append('rect')
                .attr('class', this.css.stu_bg)
                .attr('x', 0)
                .attr('y', 0)
                .attr('width', this.width)
                .attr('height', this.row_height);

            for (var j = 0; j < this.cols.length; j++) {
                var col = this.cols[j];
                var txt = this.get_txt_by_col(stu, j);

                // special rule for the study name
                var _txt = txt;
                if (j == 0) {
                    if (txt.length > 21) {
                        _txt = txt.substring(0, 21) + ' ...'
                    }
                }
                var elem = g.append('text')
                    .attr('class', this.css.txt_nm)
                    .attr('x', col.x + (col.align=='start'? 0 : col.width))
                    .attr('y', this.row_height - this.row_txtmb)
                    .attr('text-anchor', col.align)
                    .text(_txt);
                
                // bind event to the firt item
                if (j == 0) {
                    // this is the first item
                    elem.attr('pid', stu.pid);

                    // add clickable style
                    elem.attr('class', this.css.txt_nm + ' ' +
                                       this.css.txt_clickable);

                    // add title to this element
                    elem.append('title')
                        .text(txt + '. click to check the detail in PubMed');

                    // bind click
                    elem.on('click', function() {
                        // var d = d3.select(this);
                        // console.log('* clicked', d);
                        var e = $(this);
                        console.log('* clicked paper', e.attr('pid'));

                        // open something?
                        if (typeof(srv_pubmed)!='undefined') {
                            srv_pubmed.show(e.attr('pid'));
                        }
                    });
                }
            }
        }

        // the model result
        for (var i = 0; i < 1; i++) {
            var stu = this.data.model.random;
            var g = this.svg.append('g')
                .attr('class', this.css.stu_g)
                .attr('transform', 'translate(0, ' + (this.row_height * (4 + this.data.stus.length)) + ')');

            // add a background for display
            g.append('rect')
                .attr('class', this.css.stu_bg)
                .attr('x', 0)
                .attr('y', 0)
                .attr('width', this.width)
                .attr('height', this.row_height);
            for (var j = 0; j < this.cols.length; j++) {
                var col = this.cols[j];
                g.append('text')
                    .attr('class', this.css.txt_bd)
                    .attr('x', col.x + (col.align=='start'? 0 : col.width))
                    .attr('y', this.row_height - this.row_txtmb)
                    .attr('text-anchor', col.align)
                    .text(this.get_txt_by_col(stu, j));
            }
        }
    },

    _draw_heter: function() {
        // show the heterogeneity
        var g_heter = this.svg.append('g')
            .attr('transform', 'translate(0, ' + (this.row_height * (5 + this.data.stus.length)) + ')');
        var t_heter = g_heter.append('text')
            .attr('class', this.css.txt_nm)
            .attr('x', 0)
            .attr('y', this.row_height - this.row_txtmb)
            .attr('text-anchor', 'start');

        // add the subtext
        t_heter.append('tspan').text('Heterogeneity: ');
        t_heter.append('tspan').text('I').attr('class', this.css.txt_mt);
        t_heter.append('tspan').text('2').attr('class', this.css.txt_mt + ' ' + this.css.txt_sm).attr('baseline-shift', 'super');
        var txt_i2 = (this.data.heterogeneity.i2 * 100).toFixed(0) + '%';
        t_heter.append('tspan').text('=' + txt_i2);
        t_heter.append('tspan').text(', ');

        // add tau2
        t_heter.append('tspan').text('τ');
        t_heter.append('tspan').text('2').attr('class', this.css.txt_mt + ' ' + this.css.txt_sm).attr('baseline-shift', 'super');
        var txt_tau2 = (this.data.heterogeneity.tau2).toFixed(4) 
        t_heter.append('tspan').text('=' + txt_tau2);
        t_heter.append('tspan').text(', ');

        // add p
        t_heter.append('tspan').text('p').attr('class', this.css.txt_mt);
        var txt_p = (this.data.heterogeneity.p).toFixed(2) 
        t_heter.append('tspan').text('=' + txt_p);
    },

    _draw_forest: function() {
        // first, make the scale to map values to x value
        this.x_scale = d3.scaleLog()
            .domain([1e-2, 1e2])
            .range([0, this.cols[7].width]);

        this.y_scale = function(i) {
            return fg_prim_forest.row_height * (3.5 + i);
        }

        // draw the x axis
        this.xAxis = d3.axisBottom(fg_prim_forest.x_scale)
            .ticks(5, '~g')
            .tickValues([1e-2,1e-1,1e0,1e1,1e2]);
        this.svg.append('g')
            .attr('transform', 'translate('+(this.cols[7].x + this.row_frstml)+', '+(this.row_height * (6 + this.data.stus.length))+')')
            .call(this.xAxis);

        // draw the middle line
        var g_forest = this.svg.append('g')
            .attr('transform', 'translate('+(this.cols[7].x + this.row_frstml)+', 0)');

        g_forest.append('path')
            .datum([ [1, -0.5], [1, this.data.stus.length + 2.5] ])
            .attr('stroke', 'black')
            .attr('stroke-width', .8)
            .attr('d', d3.line()
                .x(function(d) { return fg_prim_forest._x_scale(d[0]); })
                .y(function(d) { return fg_prim_forest.y_scale(d[1]); })
            );

        // draw each study
        this.svg.selectAll('g.prim-frst-stu-item')
            .data(this.data.stus)
            .join("g")
            .attr('class', 'prim-frst-stu-item')
            .attr('transform', function(d, i) {
                var trans_x = fg_prim_forest.cols[7].x + fg_prim_forest.row_frstml;
                var trans_y = fg_prim_forest.y_scale(i);
                return 'translate('+trans_x+','+trans_y+')';
            })
            .each(function(d, i) {
                // console.log(i, d);
                // add the rect
                // so, first, we need to know the size for this dot
                var s = fg_prim_forest.min_dot_size + 
                    (fg_prim_forest.row_height - fg_prim_forest.min_dot_size) * d.w_random;
                var x = fg_prim_forest._x_scale(d.bt_TE) - s/2;
                var y = - s / 2;
                d3.select(this)
                    .append('rect')
                    .attr('class', 'prim-frst-stu-rect')
                    .attr('x', x)
                    .attr('y', y)
                    .attr('width', s)
                    .attr('height', s);

                // add the line
                var x1 = fg_prim_forest._x_scale(d.bt_lower);
                var x2 = fg_prim_forest._x_scale(d.bt_upper);
                d3.select(this)
                    .append('line')
                    .attr('class', 'prim-frst-stu-line')
                    .attr('x1', x1)
                    .attr('x2', x2)
                    .attr('y1', 0)
                    .attr('y2', 0);
            });

        // draw the model ref line
        var xr1 = this._x_scale(this.data.model.random.bt_TE);
        var xr2 = xr1;
        var yr1 = this.y_scale(-0.5);
        var yr2 = this.y_scale(this.data.stus.length + 2.5)
        this.svg.append('g')
            .attr('transform', 'translate('+(this.cols[7].x + this.row_frstml)+', 0)')
            .append('line')
            .attr('class', 'prim-frst-stu-model-refline')
            .attr('stroke-dasharray', '3,3')
            .attr('x1', xr1)
            .attr('x2', xr2)
            .attr('y1', yr1)
            .attr('y2', yr2);

        // draw the model diamond
        var x0 = this._x_scale(this.data.model.random.bt_lower);
        var xc = this._x_scale(this.data.model.random.bt_TE);
        var x1 = this._x_scale(this.data.model.random.bt_upper);
        var y0 = this.row_txtmb;
        var yc = this.row_height / 2;
        var y1 = this.row_height - this.row_txtmb;
        var path_d = 'M ' + 
            x0 + ' ' + yc + ' ' +
            xc + ' ' + y0 + ' ' +
            x1 + ' ' + yc + ' ' + 
            xc + ' ' + y1 + ' ' +
            'Z';

        this.svg.append('g')
            .attr('transform', 'translate('+(this.cols[7].x + this.row_frstml)+', '+(this.row_height * (4 + this.data.stus.length))+')')
            .append('path')
            .attr('d', path_d)
            .attr('class', 'prim-frst-stu-model');
    },

    get_txt_by_col: function(obj, idx) {
        switch(idx) {
            case 0: return obj.name;
            case 1: return obj.Et;
            case 2: return obj.Nt;
            case 3: return obj.Ec;
            case 4: return obj.Nc;
            case 5: return obj.bt_TE.toFixed(2);
            case 6: return '['+obj.bt_lower.toFixed(2)+'; '+obj.bt_upper.toFixed(2)+']';

            // case 7 is the figure, so no text
            case 7: return ''; 
            case 8: 
                if (obj.hasOwnProperty('w')) {
                    // this is the model
                    return '100%';
                } else {
                    return (obj['w_random'] * 100).toFixed(1) + '%';
                }
        }
        return '';
    },

    clear: function() {
        $(this.plot_id).html('');
        this.init();
    }
};