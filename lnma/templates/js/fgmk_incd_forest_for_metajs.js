var fgmk_incd_forest = {

    make_fig: function(box_id) {
    
    return {
        box_id: '#' + box_id,
        plot_id: '#'+ box_id + '_svg',
        plot_type: 'd3js',
        svg: null,
        cols: [
            {width: 150, align: 'start',  name: 'Study', x: 0, row: 2},
            {width: 50,  align: 'end',    name: 'Events', row: 2},
            {width: 50,  align: 'end',    name: 'Total', row: 2},
            {width: 100,  align: 'end',    name: 'Incidence (%)', row: 2},
            {width: 100, align: 'start',    name: '95% CI', row: 2},
            {width: 200, align: 'middle', name: 'Event Rate (95% CI)', row: 2},
            {width: 100, align: 'end',    name: 'Relative weight', row: 2}
        ],
        row_height: 15,
        min_dot_size: 4,
        row_txtmb: 3,
        row_frstml: 20,
        default_height: 300,
        max_study_name_length: 30,
    
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
            ".prim-frst-txt-clickable:hover{ fill: blue; }",
            "</style>"
        ].join('\n'),
    
        _x_scale: function(v) {
            var x = this.x_scale(v);
    
            if (x.toString() == 'NaN') {
                return 0;
            } else {
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
            console.log('* draw incd forest data', data);
            // clear the old plot first
            this.clear();
    
            // bind new data
            this.data = data;
            this.cfg = cfg;
    
            // update the height of svg according to number of studies
            // 8 is the number of lines of header and footers
            this.height = this.row_height * (data.stus.length + 8);
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
                        if (txt.length > this.max_study_name_length) {
                            _txt = txt.substring(0, this.max_study_name_length) + ' ...'
                        }
                    }
                    var col_offset_x = 0;
                    if (j == 3) {
                        col_offset_x = -10;
                    }
                    var elem = g.append('text')
                        .attr('class', this.css.txt_nm)
                        .attr('x', col.x + (col.align=='start'? 0 : col.width) + col_offset_x)
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

                    var col_offset_x = 0;
                    if (j == 3) {
                        col_offset_x = -10;
                    }

                    g.append('text')
                        .attr('class', this.css.txt_bd)
                        .attr('x', col.x + (col.align=='start'? 0 : col.width) + col_offset_x)
                        .attr('y', this.row_height - this.row_txtmb)
                        .attr('text-anchor', col.align)
                        .text(this.get_txt_by_col(stu, j));
                }
            }
        },
    
        _isna: function(v) {
            if (v === null) {
                return true;
            }
            if (v === '') {
                return true;
            }
            if (v === 'NA' || v === 'na' || v === 'Na' || v === 'nA') {
                return true;
            }
            return false;
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
            t_heter.append('tspan').text('=');
            try {
                if (this._isna(this.data.model.heterogeneity.I2)) {
                    t_heter.append('tspan').text('NA');
                } else {
                    var txt_i2 = (this.data.model.heterogeneity.I2 * 100).toFixed(0) + '%';
                    t_heter.append('tspan').text(txt_i2);
                }
            } catch (err) {
                console.log(err);
                t_heter.append('tspan').text('NA');
            }
            t_heter.append('tspan').text(', ');
    
            // add tau2
            t_heter.append('tspan').text('τ');
            t_heter.append('tspan').text('2').attr('class', this.css.txt_mt + ' ' + this.css.txt_sm).attr('baseline-shift', 'super');
            t_heter.append('tspan').text('=');
            try {
                if (this._isna(this.data.model.heterogeneity.tau2)) {
                    t_heter.append('tspan').text('NA');
                } else {
                    var txt_tau2 = (this.data.model.heterogeneity.tau2).toFixed(4) 
                    t_heter.append('tspan').text(txt_tau2);
                }
            } catch (err) {
                console.log(err);
                t_heter.append('tspan').text('NA');
            }
            t_heter.append('tspan').text(', ');
    
            // add p
            t_heter.append('tspan').text('p').attr('class', this.css.txt_mt);
            t_heter.append('tspan').text('=');
            try {
                if (this._isna(this.data.model.heterogeneity.pval_Q)) {
                    t_heter.append('tspan').text('NA');
                } else {
                    var txt_p = (this.data.model.heterogeneity.pval_Q).toFixed(2) 
                    t_heter.append('tspan').text(txt_p);
                }
            } catch (err) {
                console.log(err);
                t_heter.append('tspan').text('NA');
            }
        },
    
        _draw_forest: function() {
            // first, make the scale to map values to x value
            var x_range = [0.01, 100];
            this.set_x_scale(x_range);

            this.y_scale = (function(fig) {
                return function(i) {
                    return fig.row_height * (3.5 + i);
                }
            })(this);
    
            // draw the x axis
            this.xAxis = d3.axisBottom(this.x_scale)
                .ticks(this.x_axis_tick_values.length)
                .tickValues(this.x_axis_tick_values);
            this.svg.append('g')
                .attr('id', 'x_axis_ticks')
                .attr('transform', 'translate('+(this.cols[5].x + this.row_frstml)+', '+(this.row_height * (6 + this.data.stus.length))+')')
                .call(this.xAxis);
    
            // draw the middle line
            var g_forest = this.svg.append('g')
                .attr('transform', 'translate('+(this.cols[5].x + this.row_frstml)+', 0)');
    
            g_forest.append('path')
                .datum([ [50, -0.5], [50, this.data.stus.length + 2.5] ])
                .attr('stroke', 'black')
                .attr('stroke-width', .8)
                .attr('d', d3.line()
                    .x((function(fig) {
                        return function(d) { 
                            return fig._x_scale(d[0]); 
                        };
                    })(this))
                    .y((function(fig) {
                        return function(d) { 
                            return fig.y_scale(d[1]); 
                        };
                    })(this))
                );
    
            // draw each study
            this.svg.selectAll('g.prim-frst-stu-item')
                .data(this.data.stus)
                .join("g")
                .attr('class', 'prim-frst-stu-item')
                .attr('transform', (function(fig) {
                    return function(d, i) {
                        var trans_x = fig.cols[5].x + fig.row_frstml;
                        var trans_y = fig.y_scale(i);
                        return 'translate('+trans_x+','+trans_y+')';
                    };
                })(this))
                .each((function(fig) {
                    return function(d, i) {
                        // console.log(i, d);
                        // add the rect
                        var s = fig.min_dot_size + 
                            (fig.row_height - fig.min_dot_size) * d.w;
                        var x = fig._x_scale(d.SM * 100) - s/2;
                        var y = - s / 2;
                        d3.select(this)
                            .append('rect')
                            .attr('class', 'prim-frst-stu-rect')
                            .attr('x', x)
                            .attr('y', y)
                            .attr('width', s)
                            .attr('height', s);
        
                        // add the line
                        var _SM_lower = d.SM_lower * 100;
                        var _SM_upper = d.SM_upper * 100;
                        var x1 = fig._x_scale(_SM_lower);
                        var x2 = fig._x_scale(_SM_upper);
                        d3.select(this)
                            .append('line')
                            .attr('class', 'prim-frst-stu-line')
                            .attr('x1', x1)
                            .attr('x2', x2)
                            .attr('y1', 0)
                            .attr('y2', 0);
                    }
                })(this));
    
            // draw the model ref line
            var xr1 = this._x_scale(this.data.model.random.SM * 100);
            var xr2 = xr1;
            var yr1 = this.y_scale(-0.5);
            var yr2 = this.y_scale(this.data.stus.length + 2.5)
            this.svg.append('g')
                .attr('transform', 'translate('+(this.cols[5].x + this.row_frstml)+', 0)')
                .append('line')
                .attr('class', 'prim-frst-stu-model-refline')
                .attr('stroke-dasharray', '3,3')
                .attr('x1', xr1)
                .attr('x2', xr2)
                .attr('y1', yr1)
                .attr('y2', yr2);
    
            // draw the model diamond
            var x0 = this._x_scale(this.data.model.random.SM_lower * 100);
            var xc = this._x_scale(this.data.model.random.SM * 100);
            var x1 = this._x_scale(this.data.model.random.SM_upper * 100);
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
                .attr('transform', 'translate('+(this.cols[5].x + this.row_frstml)+', '+(this.row_height * (4 + this.data.stus.length))+')')
                .append('path')
                .attr('d', path_d)
                .attr('class', 'prim-frst-stu-model');
        },
    
        get_txt_by_col: function(obj, idx) {
            switch(idx) {
                case 0: return obj.study;
                case 1: return obj.Et;
                case 2: return obj.Nt;
                // incidence is %
                case 3: return (obj.SM * 100).toFixed(2);
                case 4: return '['+(obj.SM_lower * 100).toFixed(2)+'; ' + (obj.SM_upper * 100).toFixed(2)+']';
    
                // case 7 is the figure, so no text
                case 5: return ''; 
                case 6: 
                    return (obj.w * 100).toFixed(1) + '%';
            }
            return '';
        },
    
        clear: function() {
            $(this.plot_id).html('');
            this.init();
        },

        set_x_scale: function(x_range) {
            var diff = x_range[1] - x_range[0];
            var scale = d3.scaleLinear();
            this.x_scale = scale.domain([0, 100])
                .range([0, this.cols[5].width]);
            this.x_axis_tick_values = [0, 25, 50, 75, 100]
        }
    };
    
    
    }
    };