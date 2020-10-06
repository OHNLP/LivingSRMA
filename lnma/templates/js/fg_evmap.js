var fg_evmap = {
    plot_id: 'fg_evmap',
    cfg: {
        height: 600,
        margin_left: 180,
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
        var xs = [];
        var ys = [];
        var ss = [];
        var cs = [];
        var txts = [];

        for (var i = 0; i<this.data.data[treat].length; i++) {
            var d = this.data.data[treat][i];
            var x = d.oc;
            var y = d.t;
            var s = d.c * 12;
            var c = this.cfg.color[d.e];
            var txt = 'Treatment: ' + y + '<br>' + 
                'Comparator: ' + treat + '<br>' + 
                'Certainty: ' + this.cfg.cert2txt[d.c] + '<br>' + 
                'Effect: ' + d.e_txt;

            // append to list
            xs.push(x);
            ys.push(y);
            ss.push(s);
            cs.push(c);
            txts.push(txt);
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