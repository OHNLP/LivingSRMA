var fg_evmap = {
    plot_id: 'fg_evmap',
    cfg: {
        height: 600,
        margin_left: 220,
        margin_right: 20,
        margin_top: 20,
        opacity: 1,
        color: {
            0: '',
            1: 'red',
            2: 'gold',
            3: 'green'
        },
        cert2opacity: {
            0: 0,
            1: 0.25,
            2: 0.50,
            3: 0.75,
            4: 1
        },
        cert2txt: {
            0: 'NA',
            1: 'Very Low',
            2: 'Low',
            3: 'Moderate',
            4: 'High'
        },
        effect2txt: {
            0: 'NA',
            1: 'Significant Harm',
            2: 'No Significant Effect',
            3: 'Significant Benefit'
        },
        xaxis_title: 'Outcomes of Interest'
    },

    init: function(data, treat) {
        console.log(data);
        this.data = data;

        // treat could be null or undefined
        if (typeof(treat) == 'undefined' ||
            treat == null) {
            treat = data.treat_list[0];
        }
        if (data.treat_list.indexOf(treat)<0) {
            treat = data.treat_list[0];   
        }
        this.draw(treat);
    },

    draw: function(treat) {
        this.treat = treat;
        var treatment = treat;
        var treatment_fullname = this.data.treat_dict[treatment].tr_fullname;

        // oc list for x axis
        var oc_list = [];
        for (var oc_name in this.data.oc_dict) {
            oc_list.push(oc_name);
        }

        // treat list for y axis
        var treat_list = [];
        for (var i = 0; i < this.data.treat_list.length; i++) {
            var treat = this.data.treat_list[i];
            treat_list.push(this.data.treat_dict[treat].tr_fullname);
        }

        // to hold all the traces of all combinations.
        var trace_dict = {};

        for (var comparator in this.data.data) {
            for (var i = 0; i<this.data.data[comparator].length; i++) {
                var d = this.data.data[comparator][i];
                var x = d.oc;

                // cert == 0 and effect == 0?
                if (d.c == 0 && d.e == 0) {
                    continue;
                }

                // if the t is not the treatment we are looking for
                // then just continue
                if (d.t != treatment) {
                    continue;
                }

                var y = comparator;
                var y_fullname = this.data.treat_dict[comparator].tr_fullname;
                var s = d.c * 12;
                var c = this.cfg.color[d.e];
                var o = this.cfg.cert2opacity[d.c];
                var sm = this.data.oc_dict[x].oc_measures[0];
                var sm_val = null;
                var sm_low = null;
                var sm_upp = null;
                var has_sm = false;

                if (this.data.oc_dict[x].lgtable[sm].hasOwnProperty(comparator)) {
                    if (this.data.oc_dict[x].lgtable[sm][comparator].hasOwnProperty(treatment)) {
                        has_sm = true;
                        sm_val = this.data.oc_dict[x].lgtable[sm][comparator][treatment].sm;
                        sm_low = this.data.oc_dict[x].lgtable[sm][comparator][treatment].lw;
                        sm_upp = this.data.oc_dict[x].lgtable[sm][comparator][treatment].up;
                    }
                }
    
                var txt = 'Outcome: <b>' + this.data.oc_dict[x].oc_fullname + '</b><br>' +
                    'Comparator: <b>' + y_fullname + '</b><br>' + 
                    'Treatment: <b>' + treatment_fullname + '</b><br>' + 
                    'Certainty: <b>' + this.cfg.cert2txt[d.c] + '</b><br>' + 
                    'Effect: <b>' + d.e_txt + '</b>';

                if (has_sm) {
                    txt += "<br>" + sm + ': <b>' + sm_val.toFixed(2) + ' (' + sm_low.toFixed(2)+  ', ' + sm_upp.toFixed(2) + ')</b>';
                }

                // put this bubble to a specified group
                // first, whether this effect + cert exists?
                var trace_group_id = this._get_trace_group_id(d.e, d.c);
                if (trace_dict.hasOwnProperty(trace_group_id)) {
                    // OK, the effect array exists
                } else {
                    trace_dict[trace_group_id] = {
                        _trace_group_id: trace_group_id,
                        name: this.cfg.effect2txt[d.e] + ' (' + this.cfg.cert2txt[d.c] + ')',
                        x: [],
                        y: [],
                        mode: 'markers',
                        text: [],
                        hovertemplate: '%{text}',
                        // legendgroup: this.cfg.effect2txt[d.e],
                        marker: {
                            size: [],
                            color: [],
                            opacity: []
                        },
                        hoverlabel: {
                            font: {
                                size: 13
                            },
                            align: 'left'
                        }
                    }
                }
                // append to list
                trace_dict[trace_group_id].x.push(x);
                trace_dict[trace_group_id].y.push(y_fullname);
                trace_dict[trace_group_id].text.push(txt);
                trace_dict[trace_group_id].marker.size.push(s);
                trace_dict[trace_group_id].marker.color.push(c);
                trace_dict[trace_group_id].marker.opacity.push(o);
            }

        }
          
        // put all traces into plot data
        this.plot_data = [];
        for (var e = 3; e > 0; e--) {
            for (var c = 4; c > 0; c--) {
                var trace_group_id = this._get_trace_group_id(e, c);
                if (trace_dict.hasOwnProperty(trace_group_id)) {
                    this.plot_data.push(
                        trace_dict[trace_group_id]
                    );
                }
            }
        }
        
        // a patch trace for fix the x axis
        this.plot_data.push({
            name: '',
            x: oc_list,
            y: [],
            showlegend: false,
            visible: true
        });

        // a patch trace for fix the y axis
        this.plot_data.push({
            name: '',
            x: [],
            y: treat_list,
            showlegend: false,
            visible: true
        });
        
        // set the layout
        this.plot_layout = {
            title: '',
            hovermode: 'closest',
            showlegend: true,
            margin: {
                l: this.cfg.margin_left,
                r: this.cfg.margin_right,
                t: this.cfg.margin_top
            },
            xaxis: {
                title: this.cfg.xaxis_title,
                type: 'category',
                autorange: true,
                // 2021-04-05: fix the margin
                // https://plotly.com/javascript/reference/layout/xaxis/
                automargin: true,
                tickvals: oc_list,
                tickangle: 270
            },
            yaxis: {
                automargin: true,
                type: 'category',
                title: {
                    text: 'Comparator',
                    standoff: 10
                },
                autorange: true,
                tickvals: treat_list
            },
            legend: {
                y: 1.01,
                itemsizing: 'trace',
                itemclick: 'toggleothers',
                title: {
                    text: 'Treatment Effects',
                    font: {
                        size: 16
                    }
                }
            },
            height: this.cfg.height
        };

        this.plot_config = {
            responsive: true,
            displayModeBar: false,
            scrollZoom: false,
        }

        Plotly.newPlot(
            this.plot_id, 
            this.plot_data, 
            this.plot_layout,
            this.plot_config
        );
    },

    _get_trace_group_id: function(e, c) {
        var trace_group_id = 'E' + e + 'C' + c;
        return trace_group_id;
    }
}