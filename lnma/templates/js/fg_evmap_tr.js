var fg_evmap = {
    plot_id: 'fg_evmap',
    cfg: {
        height: 600,
        margin_left: 220,
        margin_right: 20,
        margin_top: 20,
        color: {
            0: '',
            1: 'red',
            2: 'gold',
            3: 'green'
        },
        cert2txt: {
            0: '',
            1: 'Very Low',
            2: 'Low',
            3: 'Moderate',
            4: 'High'
        },
        xaxis_title: 'Outcomes of Interest'
    },

    init: function(data, treat) {
        this.data = data;
        this.draw(treat);
    },

    draw: function(treat) {
        this.treat = treat;
        var treatment = treat;
        var treatment_fullname = this.data.treat_dict[treatment].tr_fullname;
        var xs = [];
        var ys = [];
        var ss = [];
        var cs = [];
        var txts = [];

        for (var comparator in this.data.data) {
            for (var i = 0; i<this.data.data[comparator].length; i++) {
                var d = this.data.data[comparator][i];
                var x = d.oc;

                // if the t is not the treatment we are looking for
                // then just continue
                if (d.t != treatment) {
                    continue;
                }

                var y = comparator;
                var y_fullname = this.data.treat_dict[comparator].tr_fullname;
                var s = d.c * 12;
                var c = this.cfg.color[d.e];
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
    
                var txt = 'Outcome: ' + this.data.oc_dict[x].oc_fullname + '<br>' +
                    'Comparator: ' + y_fullname + '<br>' + 
                    'Treatment: ' + treatment_fullname + '<br>' + 
                    'Certainty: ' + this.cfg.cert2txt[d.c] + '<br>' + 
                    'Effect: ' + d.e_txt;

                if (has_sm) {
                    txt += "<br>" + sm + ': ' + sm_val.toFixed(2) + ' (' + sm_low.toFixed(2)+  ', ' + sm_upp.toFixed(2) + ')';
                }
                // append to list
                xs.push(x);
                ys.push(y_fullname);
                ss.push(s);
                cs.push(c);
                txts.push(txt);
            }

        }
        var trace1 = {
            name: 'Very Low',
            x: xs,
            y: ys,
            mode: 'markers',
            text: txts,
            marker: {
                size: ss,
                color: cs,
                opacity: 1
            }
        };
          
        this.plot_data = [
            trace1
        ];
          
        this.plot_layout = {
            title: '',
            hovermode: 'closest',
            showlegend: false,
            margin: {
                l: this.cfg.margin_left,
                r: this.cfg.margin_right,
                t: this.cfg.margin_top
            },
            xaxis: {
                title: this.cfg.xaxis_title
            },
            yaxis: {
                automargin: true,
                title: {
                    text: 'Comparator',
                    standoff: 10
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
    }
}