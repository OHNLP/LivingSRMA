var fg_pscplt = {
    box: null,
    box_id: '#fg-nma-pscplt',
    chart: null,
    chart_id: 'fg-nma-pscplt-div',
    data: null,
    width: 420,
    height: 320,

    sample: {
        treats: ['Acarbose', 'Benfluorex', 'Metformin', 'Miglitol', 'Pioglitazone', 
                 'Placebo', 'Rosiglitazone', 'Sitagliptin', 'Sulfonylurea', 'Vildagliptin'],
        vals: [
            {name: 'Acarbose', vals: [0.00,0.01,0.09,0.26,0.48,0.70,0.85,0.93,0.97,1.00]},
            {name: 'Benfluorex', vals: [0.01,0.10,0.26,0.46,0.65,0.79,0.89,0.94,0.97,1.00]},
            {name: 'Metformin', vals: [0.00,0.00,0.00,0.01,0.04,0.13,0.32,0.62,0.88,1.00]},
            {name: 'Miglitol', vals: [0.00,0.01,0.06,0.15,0.31,0.51,0.70,0.82,0.92,1.00]},
            {name: 'Pioglitazone', vals: [0.00,0.00,0.01,0.04,0.09,0.20,0.36,0.57,0.77,1.00]},
            {name: 'Placebo', vals: [0.86,0.99,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00]},
            {name: 'Rosiglitazone', vals: [0.00,0.00,0.00,0.00,0.01,0.03,0.10,0.27,0.58,1.00]},
            {name: 'Sitagliptin', vals: [0.06,0.27,0.50,0.67,0.78,0.87,0.92,0.95,0.97,1.00]},
            {name: 'Sulfonylurea', vals: [0.05,0.45,0.74,0.90,0.97,0.99,1.00,1.00,1.00,1.00]},
            {name: 'Vildagliptin', vals: [0.03,0.16,0.33,0.52,0.67,0.78,0.86,0.91,0.95,1.00]}    
        ]
    },

    init: function() {
        this.box = $(this.box_id)
            .css('width', this.width);

        $(document.getElementById(this.chart_id))
            .css('width', this.width + 'px')
            .css('height', this.height + 'px');
        this.chart = echarts.init(
            document.getElementById(this.chart_id),
            null, 
            {
                renderer: 'svg'
            }
        );
        this.svg = d3.select(this.chart_id + ' svg');
    },

    clear: function() {
        this.chart.clear();
        // hide
        $(this.box_id).hide();
    },

    draw: function(data) {
        // show
        $(this.box_id).show();
        // bind data
        this.data = data;
        // create x data and values
        var treats = [];
        var values = [];
        for (let i = 0; i < data.rs.length; i++) {
            const item = data.rs[i];
            treats.push(item.treat);
            values.push(item.value);
        }
        // update option
        this.option = {
            grid: {
                top: 15,
                bottom: 65,
                right: 15
            },
            title: {
                show: false
            },
            tooltip: {
                show: true
            },
            xAxis: {
                type: 'category',
                name: '',
                nameLocation: 'middle',
                nameGap: 30,
                data: treats,
                axisLabel: {
                    rotate: 90
                }
            },
            yAxis: {
                type: 'value',
                name: 'P-Score',
                min: 0,
                max: 1
            },
            series: [{
                type: 'bar',
                data: values,
                label: {
                    show: true,
                    position: 'top',
                    formatter: function(params) {
                        // console.log(params);
                        return params.value.toFixed(2);
                    }
                },
                itemStyle: {
                    color: 'mediumaquamarine'
                },
                showBackground: true,
                backgroundStyle: {
                    color: 'rgba(220, 220, 220, 0.5)'
                }
            }]
        };
        this.chart.clear();
        this.chart.setOption(this.option, true);
    }
}