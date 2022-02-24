var fgmk_subg_forest = {

    make_fig: function(box_id) {
    
    return {
        box_id: '#'+box_id,
        plot_id: '#'+box_id+'_svg',
        plot_type: 'd3js',
        svg: null,
        cols: null,

        layout: {
            PRIM_CAT_RAW: [
                {width: 150, align: 'start',  name: 'Study', x: 0, row: 2},
                {width: 50,  align: 'end',    name: 'Events', row: 2},
                {width: 50,  align: 'end',    name: 'Total', row: 2},
                {width: 50,  align: 'end',    name: 'Events', row: 2},
                {width: 50,  align: 'end',    name: 'Total', row: 2},
        
                {width: 50,  align: 'end',    name: '$SM$', row: 2},
                {width: 100, align: 'end',    name: '95% CI', row: 2},
                {width: 200, align: 'middle', name: '$SM_NAME$ (95% CI)', row: 2},
                {width: 100, align: 'end',    name: 'Relative weight', row: 2}
            ],
            PRIM_CAT_PRE: [
                {width: 200, align: 'start',  name: 'Study', x: 0, row: 2},
                {width: 5,  align: 'end',    name: '', row: 2},
                {width: 5,  align: 'end',    name: '', row: 2},
                {width: 5,  align: 'end',    name: '', row: 2},
                {width: 5,  align: 'end',    name: '', row: 2},
        
                {width: 50,  align: 'end',    name: '$SM$', row: 2},
                {width: 100, align: 'end',    name: '95% CI', row: 2},
                {width: 250, align: 'middle', name: '$SM_NAME$ (95% CI)', row: 2},
                {width: 100, align: 'end',    name: 'Relative weight', row: 2}
            ],
        },

        row_height: 15,
        min_dot_size: 4,
        row_txtmb: 3,
        row_frstml: 20,
        // for drawing the rows, need to locate the row index
        row_idx: 1,

        // please change this accordingly
        default_height: 300,
        max_study_name_length: 30,
        
        is_draw_prediction_interval: false,
        loc: {
            prediction_interval: 5,
            heterogeneity: 5,
        },
    
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
        css_html: [
            "<style>",
            ".prim-frst-txt-bd{ font-weight: bold; }",
            ".prim-frst-txt-nm{ font-weight: normal; }",
            ".prim-frst-txt-mt{ font-family: Times; font-style: italic; }",
            ".prim-frst-txt-sm{ font-size: xx-small; }",
            ".prim-frst-stu-g text{ cursor: default; }",
            ".prim-frst-stu-bg{ fill: white; }",
            ".prim-frst-stu-rect{ fill: black; }",
            ".prim-frst-stu-line{ stroke: black; stroke-width: 1; }",
            ".prim-frst-stu-model{ stroke: black; stroke-width: 1; }",
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

            // reset the row index for drawing
            this.row_idx = 1;
            
            // reset the col start location
            if (this.cols != null) {
                for (var i = 0; i < this.cols.length; i++) {
                    var col = this.cols[i];
                    col.x = i>0? this.cols[i-1].x + this.cols[i-1].width : 0;
                    this.width += col.width;
                }
            }
            
            // set the default height this plot
            this.height = this.default_height;
    
            // init the svg
            this.svg = d3.select(this.plot_id)
                .attr('width', this.width)
                .attr('height', this.height);
        },
    
        /**
         * Draw the subgroup plots based on given input
         * 
         * @param {Object} ext The extract itself
         * @param {Object} data The data contains primma and subgs
         * @param {Object} cfg contains the config for plot
         */
        draw: function(ext, data, cfg) {
            // bind the ext data for further plot
            this.ext = ext;

            // show this figure
            $(this.box_id).show();

            // change some settings according to the raw data format
            if (cfg.params.hasOwnProperty('input_format')) {
                // set the format according the input format
                this.cols = this.layout[cfg.params.input_format];

            } else {
                // default is just using the raw
                this.cols = this.layout.PRIM_CAT_RAW;
            }
            
            // clear the old plot first
            this.clear();
    
            // bind new data
            this.data = data;
            this.cfg = cfg;
    
            // update the height of svg according to number of studies
            // this.height = this.row_height * (
            //     // the number of studies
            //     this.data.primma.stus.length + 
            //     // the number of subgroups
            //     // 1. header
            //     // 2. model
            //     // 3. heterogeneity
            //     // 4. blank margin
            //     4 * Object.keys(this.data.subgps).length + 
            //     // the number of model
            //     // 1. header
            //     // 2. blank
            //     // 3. model
            //     // 4. heterogeneity
            //     // 5. test
            //     // optional line
            //     6
            // );
            // this.svg.attr('height', this.height);
            
            // if we draw the predict interval, add one more line
            // if (this.cfg.params.prediction_interval == 'TRUE') {
            //     this.is_draw_prediction_interval = true;
            //     this.height += this.row_height;
            // } else {
            //     this.is_draw_prediction_interval = false;
            // }

            // get the range
            var range = this.get_range(this.data.primma);
            console.log(range);

            // now set the x_scale
            this.set_x_scale(range);
    
            // show header
            this._draw_header();

            // show subgroups
            var subg_idx = 0;
            var subg_colors = ['green', 'blue', 'yellow', 'pink', 'orange', 'cyan'];
            for (const subg_name in this.data.subgps.subgroups) {
                if (Object.hasOwnProperty.call(this.data.subgps.subgroups, subg_name)) {
                    const subg = this.data.subgps.subgroups[subg_name];

                    // draw the subg studies
                    this._draw_subg(subg_name, subg);

                    // draw the subg model
                    this._draw_model(
                        subg_name + ' model', 
                        subg,
                        false,
                        subg_colors[subg_idx]
                    );

                    // draw the subg model heter
                    this._draw_heter(subg.heterogeneity);

                    // increase row between groups
                    this.row_incr();

                    // increase the subg index
                    subg_idx += 1;
                }
            }
            
            // draw the overall model
            this._draw_model('main', this.data.primma, true);

            // ok, after the model, add all rest part of forest
            this.__draw_forest();

            // draw the heter of overla model
            this._draw_heter(this.data.primma.heterogeneity);

            // draw the test for subg diff
            // this._draw_subgdiff(this.data.primma.heterogeneity);
            this._draw_subgdiff(
                this.data.subgps.stat[this.cfg.params.fixed_or_random]
            );

            // draw the favours for forest
            this.__draw_favours();

            // // show the prediction interval
            // if (this.is_draw_prediction_interval) {
            //     this._draw_predition_interval();
            // }
            
            // // show the model text
            // this._draw_heter();
    
            // // show the plot
            // this._draw_forest();
    
            // finally, update the height of this svg
            this.height = this.row_height * this.row_idx;
            this.svg.attr('height', this.height);
        },

        _is_input_format: function(fmt) {
            
            if (this.cfg.params.input_format == fmt) {
                return true;
            } else {
                return false;
            }
        },

        is_input_format_cat_raw: function() {
            return this._is_input_format('PRIM_CAT_RAW');
        },
    
        _conv_col_name: function(name) {
            var ret = name;
            ret = ret.replace(/\$SM_NAME\$/g, this.cfg.sm.name);
            ret = ret.replace(/\$SM\$/g, this.cfg.sm.sm);
            return ret;
        },


        /////////////////////////////////////////////////////////////////////////
        // all kinds of drawers
        /////////////////////////////////////////////////////////////////////////
    
        _draw_header: function() {
            if (this.is_input_format_cat_raw()) {
                this.svg.append('text')
                    .attr('class', this.css.txt_bd)
                    .attr('x', this.cols[3].x)
                    .attr('y', this.row_height * this.row_idx)
                    .attr('text-anchor', "end")
                    .text('Treatment');
                
                this.svg.append('text')
                    .attr('class', this.css.txt_bd)
                    .attr('x', this.cols[5].x)
                    .attr('y', this.row_height * this.row_idx)
                    .attr('text-anchor', "end")
                    .text('Control');
                // extra text for this 
                this.row_incr(1);

            } else {

            }
            
            for (var i = 0; i < this.cols.length; i++) {
                var col = this.cols[i];
                var x = col.x + (col.align=='start'? 0 : col.align=='end'? col.width : col.width / 2);
                this.svg.append('text')
                    .attr('class', this.css.txt_bd)
                    .attr('x', x)
                    .attr('y', this.row_height * this.row_idx)
                    .attr('text-anchor', col.align)
                    .text(this._conv_col_name(col.name));
            }

            // update the index for this row
            // after drawing the header, the row index move 2 rows
            // 1 for header itself
            // 1 for the blank
            this.row_incr(2);
        },

        _draw_subg: function(subg_name, subg) {
            // draw the header of this subg
            var x = 0;
            this.svg.append('text')
                    .attr('class', this.css.txt_bd)
                    .attr('x', x)
                    .attr('y', this.row_height * this.row_idx - this.row_txtmb)
                    .attr('text-anchor', 'left')
                    .text('subgroup = ' + subg_name);
            // move the row index since drawn a new row for the header
            this.row_incr();

            // now let's draw each study
            for (var i = 0; i < subg.stus.length; i++) {
                // get this study
                var stu = subg.stus[i];

                // create a region for this study
                var g = this.svg.append('g')
                    .attr('class', this.css.stu_g)
                    .attr('transform', 'translate(0, ' + (this.row_height * (this.row_idx)) + ')');
    
                // add a background for display
                g.append('rect')
                    .attr('class', this.css.stu_bg)
                    .attr('x', 0)
                    .attr('y', -this.row_height)
                    .attr('width', this.width)
                    .attr('height', this.row_height);
    
                // now draw the columns for this study
                for (var j = 0; j < this.cols.length; j++) {
                    var col = this.cols[j];
                    var txt = this.get_txt_by_col(stu, j);
    
                    // special rule for the study name for limiting the max width
                    var _txt = txt;
                    if (j == 0) {
                        if (txt.length > this.max_study_name_length) {
                            _txt = txt.substring(0, this.max_study_name_length) + ' ...'
                        }
                    }

                    // draw the text for this column
                    var elem = g.append('text')
                        .attr('class', this.css.txt_nm)
                        .attr('x', col.x + (col.align=='start'? 0 : col.width))
                        .attr('y', -this.row_txtmb)
                        // .attr('y', this.row_height - this.row_txtmb)
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
                        if (stu.hasOwnProperty('pid')) {
                            txt = txt + ' ('+stu.pid+')';
                        }
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

                // now draw the tree in the forest
                this.__draw_tree(stu);

                // for each study, update the row_idx
                this.row_incr();;
            }

        },

        _draw_model: function(model_name, obj, enable_refline, diamond_color) {
            if (typeof(enable_refline)=='undefined') {
                enable_refline = false;
            }
            if (typeof(diamond_color)=='undefined') {
                diamond_color = 'red';
            }

            var g = this.svg.append('g')
                .attr('class', this.css.stu_g)
                .attr('transform', 'translate(0, ' + (this.row_height * this.row_idx) + ')');

            // add a background for display
            g.append('rect')
                .attr('class', this.css.stu_bg)
                .attr('x', 0)
                .attr('y', -this.row_height)
                .attr('width', this.width)
                .attr('height', this.row_height);

            // draw the cols
            for (var j = 0; j < this.cols.length; j++) {
                var col = this.cols[j];
                g.append('text')
                    .attr('class', this.css.txt_bd)
                    .attr('x', col.x + (col.align=='start'? 0 : col.width))
                    .attr('y', 0)
                    // .attr('y', this.row_height - this.row_txtmb)
                    .attr('text-anchor', col.align)
                    .text(this.get_txt_by_col(obj.model[this.cfg.params.fixed_or_random], j));
            }

            // draw the tree for this
            // this.__draw_tree(obj.model[this.cfg.params.fixed_or_random]);
            this.__draw_diamond(
                obj.model[this.cfg.params.fixed_or_random],
                enable_refline,
                diamond_color
            );

            // increase to next line
            this.row_incr();

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
    
        _draw_predition_interval: function() {
            var loc = this.data.stus.length + this.loc.prediction_interval;
            var g_predintv = this.svg.append('g')
                .attr('transform', 'translate(0, ' + (this.row_height * loc) + ')');
            var t_predintv = g_predintv.append('text')
                .attr('class', this.css.txt_nm)
                .attr('x', 0)
                .attr('y', this.row_height - this.row_txtmb)
                .attr('text-anchor', 'start');
            // add the subtext
            t_predintv.append('tspan').text('Prediction Interval:');
    
            // get the text
            var _txt = '[' + 
                this.data.model[this.cfg.params.fixed_or_random].bt_pred_lower.toFixed(2) + 
                '; ' +
                this.data.model[this.cfg.params.fixed_or_random].bt_pred_upper.toFixed(2) + 
            ']';
            // draw the lower and upper
            var col = this.cols[6];
            var elem = g.append('text')
                .attr('class', this.css.txt_nm)
                .attr('x', col.x + (col.align=='start'? 0 : col.width))
                .attr('y', this.row_height - this.row_txtmb)
                .attr('text-anchor', col.align)
                .text(_txt);
        },
    
        _draw_heter: function(heter) {
    
            // create the region
            var g_heter = this.svg.append('g')
                .attr('transform', 'translate(0, ' + (this.row_height * this.row_idx) + ')');

            // the text for heter
            var t_heter = g_heter.append('text')
                .attr('class', this.css.txt_nm)
                .attr('x', 0)
                .attr('y', 0)
                // .attr('y', this.row_height - this.row_txtmb)
                .attr('text-anchor', 'start');
    
            // add the subtext
            t_heter.append('tspan').text('Heterogeneity: ');
            t_heter.append('tspan').text('I').attr('class', this.css.txt_mt);
            t_heter.append('tspan').text('2').attr('class', this.css.txt_mt + ' ' + this.css.txt_sm).attr('baseline-shift', 'super');
            t_heter.append('tspan').text('=');
            try {
                if (this._isna(heter.i2)) {
                    t_heter.append('tspan').text('NA');
                } else {
                    var txt_i2 = (heter.i2 * 100).toFixed(0) + '%';
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
                if (this._isna(heter.tau2)) {
                    t_heter.append('tspan').text('NA');
                } else {
                    var txt_tau2 = (heter.tau2).toFixed(4) 
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
                if (this._isna(heter.p)) {
                    t_heter.append('tspan').text('NA');
                } else {
                    var txt_p = (heter.p).toFixed(2) 
                    t_heter.append('tspan').text(txt_p);
                }
            } catch (err) {
                console.log(err);
                t_heter.append('tspan').text('NA');
            }

            this.row_incr();
        },
    
        _draw_subgdiff: function(stat) {
    
            // create the region
            var g_sdiff = this.svg.append('g')
                .attr('transform', 'translate(0, ' + (this.row_height * this.row_idx) + ')');

            // the text for heter
            var t_texts = g_sdiff.append('text')
                .attr('class', this.css.txt_nm)
                .attr('x', 0)
                .attr('y', 0)
                // .attr('y', this.row_height - this.row_txtmb)
                .attr('text-anchor', 'start');
    
            // add the x^2
            t_texts.append('tspan').text('Test for subgroup differences: ');
            t_texts.append('tspan').text('X').attr('class', this.css.txt_mt);
            t_texts.append('tspan').text('2').attr('class', this.css.txt_mt + ' ' + this.css.txt_sm).attr('baseline-shift', 'super');
            t_texts.append('tspan').text('1').attr('class', this.css.txt_mt + ' ' + this.css.txt_sm).attr('baseline-shift', 'sub').attr('dx', '-4');
            t_texts.append('tspan').text('=');
            try {
                if (this._isna(stat.Q_b)) {
                    t_texts.append('tspan').text('NA');
                } else {
                    var txt = (stat.Q_b * 100).toFixed(0) + '%';
                    t_texts.append('tspan').text(txt);
                }
            } catch (err) {
                console.log(err);
                t_texts.append('tspan').text('NA');
            }
            t_texts.append('tspan').text(', ');
    
            // add df
            t_texts.append('tspan').text('df=');
            try {
                if (this._isna(stat.df_Q)) {
                    t_texts.append('tspan').text('NA');
                } else {
                    var txt = (stat.df_Q).toFixed(4) 
                    t_texts.append('tspan').text(txt);
                }
            } catch (err) {
                console.log(err);
                t_texts.append('tspan').text('NA');
            }
            t_texts.append('tspan').text(', ');
    
            // add p
            t_texts.append('tspan').text('(');
            t_texts.append('tspan').text('p').attr('class', this.css.txt_mt);
            t_texts.append('tspan').text('=');
            try {
                if (this._isna(stat.pval_Q_b)) {
                    t_texts.append('tspan').text('NA');
                } else {
                    var txt_p = (stat.pval_Q_b).toFixed(2) 
                    t_texts.append('tspan').text(txt_p);
                }
            } catch (err) {
                console.log(err);
                t_texts.append('tspan').text('NA');
            }
            t_texts.append('tspan').text(')');

            this.row_incr();
        },

        __draw_tree: function(stu) {
            if (stu.bt_TE == null) {
                // which means this doesn't have any result 
                return;
            }
            // create a region for this tree
            var gx = this.cols[7].x + this.row_frstml;
            var gy = this.row_height * this.row_idx;
            var g = this.svg.append('g')
                .attr('transform', 'translate('+gx+','+gy+')');

            // mapping the sm to the value
            // var s = 10;
            var s = this.min_dot_size + 
                (this.row_height - this.min_dot_size) * 
                stu['w_'+ this.cfg.params.fixed_or_random];

            var x = this._x_scale(stu.bt_TE) - s/2;
            var y = -this.row_height / 2;

            // now draw the circle
            g.append('rect')
                .attr('class', 'prim-frst-stu-rect')
                .attr('x', x)
                .attr('y', y - s/2)
                .attr('width', s)
                .attr('height', s);

            // now draw the line
            var x1 = this._x_scale(stu.bt_lower);
            var x2 = this._x_scale(stu.bt_upper);
            g.append('line')
                .attr('class', 'prim-frst-stu-line')
                .attr('x1', x1)
                .attr('x2', x2)
                .attr('y1', y)
                .attr('y2', y);
        },

        __draw_diamond: function(model, enable_refline, diamond_color) {
            if (typeof(enable_refline)=='undefined') {
                enable_refline = false;
            }
            if (typeof(diamond_color)=='undefined') {
                diamond_color = 'red';
            }
            // create a region
            var gx = this.cols[7].x + this.row_frstml;
            var gy = this.row_height * this.row_idx;
            var g = this.svg.append('g')
                .attr('transform', 'translate('+gx+', '+gy+')');

            // draw the model diamond
            var x0 = this._x_scale(model.bt_lower);
            var xc = this._x_scale(model.bt_TE);
            var x1 = this._x_scale(model.bt_upper);
            var y0 = this.row_txtmb - this.row_height;
            var yc = this.row_height / 2 - this.row_height;
            var y1 = this.row_height - this.row_txtmb - this.row_height;
            var path_d = 'M ' + 
                x0 + ' ' + yc + ' ' +
                xc + ' ' + y0 + ' ' +
                x1 + ' ' + yc + ' ' + 
                xc + ' ' + y1 + ' ' +
                'Z';
    
            // draw it!
            g.append('path')
                .attr('d', path_d)
                .attr('class', 'prim-frst-stu-model')
                .attr('fill', diamond_color);

            // draw the model ref line
            if (enable_refline) {
                var xr1 = this._x_scale(model.bt_TE);
                var xr2 = xr1;
                var yr1 = - this.row_height * (this.row_idx - 3);
                var yr2 = 0;
                g.append('line')
                    .attr('class', 'prim-frst-stu-model-refline')
                    .attr('stroke-dasharray', '3,3')
                    .attr('x1', xr1)
                    .attr('x2', xr2)
                    .attr('y1', yr1)
                    .attr('y2', yr2);
            }
        },

        __draw_forest: function() {
            // create a region
            var gx = this.cols[7].x + this.row_frstml;
            // the gy is a little higher than other g to make it closer to forest
            var gy = this.row_height * (this.row_idx - 0.5);
            var g = this.svg.append('g')
                .attr('transform', 'translate('+gx+', '+gy+')');

            // draw the x axis
            this.xAxis = d3.axisBottom(this.x_scale)
                .ticks(this.x_axis_tick_values.length, '~g')
                .tickValues(this.x_axis_tick_values);
            g.call(this.xAxis);
    
            // draw the middle line
            var x1 = this._x_scale(1);
            var x2 = this._x_scale(1);
            var y1 = - this.row_height * (this.row_idx - 3);
            var y2 = 0;
            g.append('line')
                .attr('class', 'prim-frst-stu-line')
                .attr('x1', x1)
                .attr('x2', x2)
                .attr('y1', y1)
                .attr('y2', y2);
        },

        __draw_favours: function() {
            // create a region
            var gx = this.cols[7].x + this.row_frstml;
            // the gy is a little higher than other g to make it closer to forest
            var gy = this.row_height * (this.row_idx);
            var g = this.svg.append('g')
                .attr('transform', 'translate('+gx+', '+gy+')');

            // text treat name
            g.append('text')
                .attr('class', this.css.txt_nm)
                .attr('x', 0)
                .attr('y', -this.row_txtmb)
                .attr('text-anchor', 'start')
                .text('Favours ' + this.ext.meta.treatments[0]);

            // text control name
            g.append('text')
                .attr('class', this.css.txt_nm)
                .attr('x', this.cols[7].width)
                .attr('y', -this.row_txtmb)
                .attr('text-anchor', 'end')
                .text('Favours ' + this.ext.meta.treatments[1]);

            
        },
    
        __do_not_use_this_draw_forest: function() {
            // first, make the scale to map values to x value
            this.x_scale = d3.scaleLog()
                .domain([1e-2, 1e2])
                .range([0, this.cols[7].width]);
    
            this.y_scale = (function(fig){
                return function(i) {
                    return fig.row_height * (3.5 + i);
                }
            })(this);
    
            // draw the x axis
            this.xAxis = d3.axisBottom(this.x_scale)
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
                    .x((function(fig) {
                        return function(d) { 
                            return fig._x_scale(d[0]); 
                        }
                    })(this))
                    .y((function(fig){
                        return function(d) { 
                            return fig.y_scale(d[1]);
                        }
                    })(this))
                );
    
            // draw each study
            this.svg.selectAll('g.prim-frst-stu-item')
                .data(this.data.stus)
                .join("g")
                .attr('class', 'prim-frst-stu-item')
                .attr('transform', (function(fig){
                    return function(d, i) {
                        var trans_x = fig.cols[7].x + fig.row_frstml;
                        var trans_y = fig.y_scale(i);
                        return 'translate('+trans_x+','+trans_y+')';
                    }
                })(this))
                .each((function(fig) {
                    return function(d, i) {
                        // console.log(i, d);
                        // add the rect
                        var s = fig.min_dot_size + 
                            (fig.row_height - fig.min_dot_size) * d['w_'+fig.cfg.params.fixed_or_random];
                    
                        var x = fig._x_scale(d.bt_TE) - s/2;
                        var y = - s / 2;
                        d3.select(this)
                            .append('rect')
                            .attr('class', 'prim-frst-stu-rect')
                            .attr('x', x)
                            .attr('y', y)
                            .attr('width', s)
                            .attr('height', s);
        
                        // add the line
                        var x1 = fig._x_scale(d.bt_lower);
                        var x2 = fig._x_scale(d.bt_upper);
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
            var xr1 = this._x_scale(this.data.model[this.cfg.params.fixed_or_random].bt_TE);
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
            var x0 = this._x_scale(this.data.model[this.cfg.params.fixed_or_random].bt_lower);
            var xc = this._x_scale(this.data.model[this.cfg.params.fixed_or_random].bt_TE);
            var x1 = this._x_scale(this.data.model[this.cfg.params.fixed_or_random].bt_upper);
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
                        if (stu.hasOwnProperty('pid')) {
                            txt = txt + ' ('+stu.pid+')';
                        }
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
                var stu = this.data.model[this.cfg.params.fixed_or_random];
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
    
        get_txt_by_col: function(obj, idx) {
            var toFixed2 = function(v) {
                if (v == null) {
                    return 'NA';
                } else {
                    return v.toFixed(2);
                }
            }
            switch(idx) {
                case 0: return obj.name;
                case 1: return obj.Et;
                case 2: return obj.Nt;
                case 3: return obj.Ec;
                case 4: return obj.Nc;
                case 5: return toFixed2(obj.bt_TE);
                case 6: return '['+
                    toFixed2(obj.bt_lower)+'; '+
                    toFixed2(obj.bt_upper)+
                    ']';
    
                // case 7 is the figure, so no text
                case 7: return ''; 
                case 8: 
                    if (obj.hasOwnProperty('w')) {
                        // this is the model
                        return '100%';
                    } else {
                        return (obj['w_' + this.cfg.params.fixed_or_random] * 100).toFixed(1) + '%';
                    }
            }
            return '';
        },
    
        clear: function() {
            $(this.plot_id).html('');
            this.init();
        },

        hide: function() {
            $(this.box_id).hide();
        },

        row_incr: function(n) {
            if (typeof(n)=='undefined') {
                n = 1;
            }
            this.row_idx += n;

            console.log('* row_idx->' + this.row_idx);
        },

        get_range: function(obj) {
            var min = 1;
            var max = 2;

            // copy a new value
            var rst = JSON.parse(JSON.stringify(obj));
            
            // put the model into stus for easy loop
            rst.stus.push(rst.model);

            // check each
            for (let i = 0; i < rst.stus.length; i++) {
                const stu = rst.stus[i];
                if (stu.bt_lower < min) {
                    min = stu.bt_lower;
                }
                if (stu.bt_upper > max) {
                    max = stu.bt_upper;
                }
            }

            return [min, max];
        },

        set_x_scale: function(y_range) {
            // the min can be 0.01
            // the max can be 10
            var diff = y_range[1] - y_range[0];

            // if the diff is less than 2
            var range = [0.1, 2];
            var ticks = [0.1, 1, 2];
            var scale = d3.scaleLinear();

            if (diff < 2) {
                // nothing, just use default
            } else if (diff < 10) {
                // oh, it's pretty large
                scale = d3.scaleLog();
                range = [0.1, 10];
                ticks = [0.1, 1, 10];
            } else {
                // oh, it's pretty large
                scale = d3.scaleLog();
                range = [0.01, 100];
                ticks = [0.01, 0.1, 1, 10, 100];
            }
            
            // set the scale
            this.x_scale = scale.domain(range)
                .range([0, this.cols[7].width]);

            // set the tick values
            this.x_axis_tick_values = ticks;
        }
    };
    }
}