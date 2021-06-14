var fgmk_cumu_forest = {

make_fig: function(box_id) {

return {
    box_id: '#' + box_id,
    plot_id: '#' + box_id + '_svg',
    plot_type: 'd3js',
    svg: null,
    cols: [
        {width: 200, align: 'start',  name: 'Study', x: 0, row: 1},
        {width: 200, align: 'middle', name: '$SM_NAME$ (95% CI)', row: 1},
        {width: 50,  align: 'end',    name: '$SM$', row: 1},
        {width: 100, align: 'end',    name: '95% CI', row: 1}
    ],
    row_height: 15,
    row_txtmb: 3,
    row_frstml: 20,
    default_height: 300,
    mark_size: 6,

    // the attribute name for drawing
    attr_TE: 'bt_TE',
    attr_lower: 'bt_lower',
    attr_upper: 'bt_upper',

    css: {
        txt_bd: 'cumu-frst-txt-bd',
        txt_nm: 'cumu-frst-txt-nm',
        txt_mt: 'cumu-frst-txt-mt',
        txt_sm: 'cumu-frst-txt-sm',
        txt_clickable: 'cumu-frst-txt-clickable',
        stu_g: 'cumu-frst-stu-g',
        stu_bg: 'cumu-frst-stu-bg',
        stu_rect: 'cumu-frst-stu-rect'
    },
    css_html: ["<style>",
        ".cumu-frst-txt-bd{ font-weight: bold; }",
        ".cumu-frst-txt-nm{ font-weight: normal; }",
        ".cumu-frst-txt-mt{ font-family: Times; font-style: italic; }",
        ".cumu-frst-txt-sm{ font-size: xx-small; }",
        ".cumu-frst-stu-g text{ cursor: default; }",
        ".cumu-frst-stu-bg{ fill: white; }",
        ".cumu-frst-stu-rect{ fill: black; }",
        ".cumu-frst-stu-line{ stroke: black; stroke-width: 1.5; }",
        ".cumu-frst-stu-model{ fill: red; stroke: black; stroke-width: 1; }",
        ".cumu-frst-stu-model-refline{ stroke: black; stroke-width: 1; }",
        ".cumu-frst-stu-g:hover .cumu-frst-stu-bg{ fill: whitesmoke; }",
        ".cumu-frst-txt-clickable{ fill: #00397b; cursor: pointer !important; }",
        ".cumu-frst-txt-clickable:hover{ fill: blue; }",
        "</style>"
    ].join('\n'),

    sample: {
        "model": {
        "random": {
            "TE": -0.5217,
            "lower": 0.411,
            "name": "Random effects model",
            "seTE": 0.1878,
            "sm": 0.594,
            "upper": 0.858
        }
        },
        "stus": [
        {
            "TE": -0.3978,
            "lower": 0.442,
            "name": "Adding Raskob et al (k=1)",
            "seTE": 0.2135,
            "sm": 0.672,
            "upper": 1.021
        },
        {
            "TE": -0.4875,
            "lower": 0.422,
            "name": "Adding Young et al (k=2)",
            "seTE": 0.1918,
            "sm": 0.614,
            "upper": 0.894
        },
        {
            "TE": -0.7358,
            "lower": 0.24,
            "name": "Adding McBane et al (k=3)",
            "seTE": 0.3526,
            "sm": 0.479,
            "upper": 0.956
        },
        {
            "TE": -0.5217,
            "lower": 0.411,
            "name": "Adding Young et al (k=4)",
            "seTE": 0.1878,
            "sm": 0.594,
            "upper": 0.858
        }
        ]
    },

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
        // clear the old plot first
        this.clear();

        // if data is null, skip
        // because this no data
        if (data === null) {
            $(this.plot_id).html('<text y="10">There are not enough records for the cumulative plot</text>');
            return;
        }

        // bind new data
        this.data = data;
        this.cfg = cfg;

        if (this.cfg.mode == 'pwma_incd') {
            this.attr_TE = 'bt_ab_TE';
            this.attr_lower = 'bt_ab_lower';
            this.attr_upper = 'bt_ab_upper';
        } else {
            this.attr_TE = 'bt_TE';
            this.attr_lower = 'bt_lower';
            this.attr_upper = 'bt_upper';
        }

        // update the height of svg according to number of studies
        // 6 is the number of lines of header and footers
        this.height = this.row_height * (this.data.stus.length + 6.5);
        this.svg.attr('height', this.height);

        // show header
        this._draw_header();
        
        // show studies
        this._draw_study_vals();

        // show the plot
        this._draw_forest();

    },

    _draw_header: function() {
        
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
                .attr('transform', 'translate(0, ' + (this.row_height * (2 + i)) + ')');

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
                    if (txt.length > 33) {
                        _txt = txt.substring(0, 32) + ' ...'
                    }
                }

                var elem = g.append('text')
                    .attr('class', this.css.txt_nm)
                    .attr('x', col.x + (col.align=='start'? 0 : col.width))
                    .attr('y', this.row_height - this.row_txtmb)
                    .attr('text-anchor', col.align)
                    .text(_txt);

                // bind event to the first col
                if (j == 0) {
                    // this is the first col
                    elem.attr('pid', stu.pid);

                    // add clickable style
                    elem.attr('class', this.css.txt_nm + ' ' +
                                       this.css.txt_clickable);

                    // add title to this element
                    elem.append('title')
                        .text(txt);

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
                .attr('transform', 'translate(0, ' + (this.row_height * (3 + this.data.stus.length)) + ')');

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

    _draw_forest: function() {
        // first, make the scale to map values to x value
        this.x_scale = d3.scaleLog()
            .domain([1e-2, 1e2])
            .range([0, this.cols[1].width]);

        this.y_scale = (function(fig) {
            return function(i) {
                return fig.row_height * (2.5 + i);
            }
        })(this);

        // draw the x axis
        this.xAxis = d3.axisBottom(this.x_scale)
            .ticks(5, '~g')
            .tickValues([1e-2,1e-1,1e0,1e1,1e2]);
        this.svg.append('g')
            .attr('transform', 'translate('+(this.cols[1].x + this.row_frstml)+', '+(this.row_height * (5 + this.data.stus.length))+')')
            .call(this.xAxis);

        // draw the middle line
        var g_forest = this.svg.append('g')
            .attr('transform', 'translate('+(this.cols[1].x + this.row_frstml)+', 0)');

        g_forest.append('path')
            .datum([ [1, -0.5], [1, this.data.stus.length + 2.5] ])
            .attr('id', 'middle_line')
            .attr('stroke', 'black')
            .attr('stroke-width', .8)
            .attr('d', d3.line()
                .x((function(fig) {
                    return function(d) { 
                        return fig._x_scale(d[0]); 
                    }
                })(this))
                .y((function(fig) {
                    return function(d) { 
                        return fig.y_scale(d[1]); 
                    }
                })(this))
            );

        // draw each study
        this.svg.selectAll('g.cumu-frst-stu-item')
            .data(this.data.stus)
            .join("g")
            .attr('class', 'cumu-frst-stu-item')
            .attr('transform', (function(fig) {
                return function(d, i) {
                    var trans_x = fig.cols[1].x + fig.row_frstml;
                    var trans_y = fig.y_scale(i);
                    return 'translate('+trans_x+','+trans_y+')';
                }
            })(this))
            .each((function(fig) {
                return function(d, i) {
                    // console.log(i, d);
                    // add the rect
                    var s = fig.mark_size;
                    var x = fig._x_scale(d[fig.attr_TE]) - s/2;
                    var y = - s / 2;
                    d3.select(this)
                        .append('rect')
                        .attr('class', 'cumu-frst-stu-rect')
                        .attr('x', x)
                        .attr('y', y)
                        .attr('width', s)
                        .attr('height', s);
    
                    // add the line
                    var x1 = fig._x_scale(d[fig.attr_lower]);
                    var x2 = fig._x_scale(d[fig.attr_upper]);
                    d3.select(this)
                        .append('line')
                        .attr('class', 'cumu-frst-stu-line')
                        .attr('x1', x1)
                        .attr('x2', x2)
                        .attr('y1', 0)
                        .attr('y2', 0);
                }
            })(this));

        // draw the model ref line
        var xr1 = this._x_scale(this.data.model.random[this.attr_TE]);
        var xr2 = xr1;
        var yr1 = this.y_scale(-0.5);
        var yr2 = this.y_scale(this.data.stus.length + 2.5)
        this.svg.append('g')
            .attr('transform', 'translate('+(this.cols[1].x + this.row_frstml)+', 0)')
            .append('line')
            .attr('class', 'cumu-frst-stu-model-refline')
            .attr('stroke-dasharray', '3,3')
            .attr('x1', xr1)
            .attr('x2', xr2)
            .attr('y1', yr1)
            .attr('y2', yr2);

        // draw the model diamond
        var x0 = this._x_scale(this.data.model.random[this.attr_lower]);
        var xc = this._x_scale(this.data.model.random[this.attr_TE]);
        var x1 = this._x_scale(this.data.model.random[this.attr_upper]);
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
            .attr('transform', 'translate('+(this.cols[1].x + this.row_frstml)+', '+(this.row_height * (3 + this.data.stus.length))+')')
            .append('path')
            .attr('d', path_d)
            .attr('class', 'cumu-frst-stu-model');
    },

    get_txt_by_col: function(obj, idx) {
        switch(idx) {
            case 0: return obj.name;
            // case 1 is the figure, so no text
            case 1: return '';
            case 2: return obj[this.attr_TE].toFixed(2);
            case 3: return '['+obj[this.attr_lower].toFixed(2)+'; '+obj[this.attr_upper].toFixed(2)+']';
        }
        return '';
    },

    clear: function() {
        $(this.plot_id).html('');
        this.init();
    }
};// end of fig obj
} // end of make_fig
} // end of fgmk_cumu_forest