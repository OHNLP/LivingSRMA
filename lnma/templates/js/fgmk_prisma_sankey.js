var fgmk_prisma_sankey = {

make_fig: function(box_id, prisma) {
    var fig = {
        box_id: '#' + box_id,
        plot_id: box_id + '_chart',

        // for the echart option
        option: {
            tooltip: {
                trigger: 'item',
                formatter: function(params) {
                    // console.log()
                    if (params.dataType == 'node') {
                        return params.data.label + ' (n=' + params.data.n + ')';
                    } else {
                        return params.data.label;
                    }
                }
            },
            animation: false,
            series: [
                {
                    type: 'sankey',
                    emphasis: {
                        focus: 'adjacency'
                    },
                    top: '8%',
                    left: '2%',
                    right: '2%',
                    data: [
                        {name: 's0', label: 'Records identified through search', n: 0, itemStyle: { color: '#aaaaaa'}},
                        {name: 'e1', label: 'Excluded duplicates', n: 0, itemStyle: { color: '#ee0000'}},
                        {name: 'a2', label: 'Records identified after remove duplicates', n: 0, itemStyle: { color: '#aaaaaa'}},
                        {name: 'a1', label: 'Records identified through auto update', n: 0, itemStyle: { color: '#aaaaaa'}},
                        {name: 'all', label: 'Records identified for screening', n: 0, itemStyle: { color: '#aaddff'}},
                        {name: 'e2', label: 'Excluded by title', n: 0, itemStyle: { color: '#ee0000'}},
                        {name: 'e22', label: 'Excluded by abstract', n: 0, itemStyle: { color: '#ee0000'}},
                        {name: 'fte', label: 'Eligible for full-text review', n: 0, itemStyle: { color: '#00ddff'}},
                        {name: 'uns', label: 'Unscreened', n: 0, itemStyle: { color: '#0000ee'}},
                        {name: 'e3', label: 'Excluded by full-text', n: 0, itemStyle: { color: '#ee0000'}},
                        {name: 'unr', label: 'Reviewing', n: 0, itemStyle: { color: '#0000ee'}},
                        {name: 'f1', label: 'Included in SR', n: 0, itemStyle: { color: '#00ee00'}},
                        {name: 'f3', label: 'Included in MA', n: 0, itemStyle: { color: '#00ee00'}},
                        {name: 'f3n', label: 'Not in MA', n: 0, itemStyle: { color: '#aaaaaa'}}
                    ],
                    links: [
                        {source: 's0', target: 'e1', label: 'Exclude by duplicates', value: 2},
                        {source: 's0', target: 'a2', label: 'Removed duplicates', value: 7},
                        {source: 'a2', target: 'all', label: 'Merged for screening from searches', value: 7},
                        {source: 'a1', target: 'all', label: 'Merged for screening from auto updates', value: 8},
                        {source: 'all', target: 'e2', label: 'Exclude by checking title', value: 2},
                        {source: 'all', target: 'e22', label: 'Exclude by checking abstract', value: 2},
                        {source: 'all', target: 'fte', label: 'Need to check full-text', value: 7},
                        {source: 'all', target: 'uns', label: 'Not checked yet', value: 4},
                        {source: 'fte', target: 'e3', label: 'Exclude by reviewing full text', value: 2},
                        {source: 'fte', target: 'f1', label: 'Include after checking full text', value: 3},
                        {source: 'fte', target: 'unr', label: 'Reviewing full text', value: 2},
                        {source: 'f1', target: 'f3', label: 'Extract data for meta-analysis', value: 2},
                        {source: 'f1', target: 'f3n', label: 'Not used in MA', value: 1}
                    ],
                    orient: 'vertical',
                    nodeAlign: 'left',
                    label: {
                        position: 'top',
                        formatter: function(params) {
                            return params.data.label + '\nn=' + params.data.n;
                        }
                    },
                    lineStyle: {
                        color: 'source',
                        curveness: 0.5
                    }
                }
            ]
        }
    };

    // update the option by the given prisma
    for (let i = 0; i < fig.option.series[0].data.length; i++) {
        const name = fig.option.series[0].data[i].name;
        
        if (prisma.stat.hasOwnProperty(name)) {
            fig.option.series[0].data[i].n = prisma.stat[name].n;
        }
    }

    // update the link option by the given prisma
    for (let i = 0; i < fig.option.series[0].links.length; i++) {
        const target = fig.option.series[0].links[i].target;
        
        if (prisma.stat.hasOwnProperty(target)) {
            fig.option.series[0].links[i].n = prisma.stat[target].n;
        }
    }

    // create the echart
    fig.chart = echarts.init(document.getElementById(fig.plot_id));
    fig.chart.setOption(fig.option);

    // bind click event
    fig.chart.on('click', function(params) {
        console.log('* clicked ' + params);
    });

    return fig;
}
}