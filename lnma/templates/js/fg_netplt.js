
var fg_netplt = {
    box: null,
    box_id: '#fg-nma-netplt',
    svg: null,
    svg_id: '#fg-nma-netplt-svg',
    data: {
        nodes: [],
        links: []
    },

    sample: {
        nodes: [
            { name: 'Ate', value: 3 }, { name: 'AteBev', value: 2 }, { name: 'Cabo', value: 2 }, 
            { name: 'Suni', value: 2 }, { name: 'NivoIpi', value: 4 }, { name: 'PemAxi', value: 2 }, 
            { name: 'Placebo', value: 2 }, { name: 'Rosi', value: 4 }, { name: 'Vilda', value: 1 }, 
            { name: 'Sulfo', value: 1 }
        ],
        links: [
            { source: 'Ate', target: 'Suni', value: 1 },
            { source: 'AteBev', target: 'Suni', value: 3 },
            { source: 'Cabo', target: 'Suni', value: 1 },
            { source: 'NivoIpi', target: 'Suni', value: 4 },
            { source: 'PemAxi', target: 'Suni', value: 2 },
            { source: 'Placebo', target: 'Suni', value: 2 },
            { source: 'Rosi', target: 'Suni', value: 2 },
            { source: 'Vilda', target: 'Suni', value: 2 },
            { source: 'Sulfo', target: 'Suni', value: 2 },
            { source: 'Vilda', target: 'Sulfo', value: 1 }
        ]
    },
    n_nodes: 0,
    width: 340,
    height: 300,
    r: 120,
    
    init: function() {
        this.r = Math.min(this.width, this.height) / 2.5;
        this.box = $(this.box_id)
            .css('width', this.width);

        this.svg = d3.select(this.svg_id)
            .attr('width', this.width)
            .attr('height', this.height);
        this.x_scale = d3.scaleLinear()
            .domain([0, 1])
            .range([this.width/2 - (this.width - this.r * 2) / 4, 
                    this.width/2 + this.r - (this.width - this.r * 2) / 4]);
        this.y_scale = d3.scaleLinear()
            .domain([0, 1])
            .range([this.height/2 , 
                    this.height/2 + this.r]);
        this.node2idx = {};

        this.tip = d3.tip()
            .attr('class', 'd3-tip')
            .direction('e')
            .offset([0,5])
            .html(function(d) {
                console.log(d);
                var content = "<div><b>" + d.name + "</b></div>" +
                    "  <div>No. of studies: " + d.value + "</div>"
                return content;
            });
        this.svg.call(this.tip);

    },

    clear: function() {
        this.svg.selectAll('*').remove();
        // hide
        $(this.box_id).hide();
    },  

    draw: function(data) {
        // show
        $(this.box_id).show();
        this.data = data;
        this.n_nodes = data.nodes.length;
        this.node2idx = {};
        for (let i = 0; i < this.data.nodes.length; i++) {
            const node = this.data.nodes[i];
            this.node2idx[node.name] = i;
        }

        // remove all old nodes and links
        this.svg.selectAll("*").remove();

        // draw new links first, since svg didn't support z-index
        var links = this.svg.selectAll('.line')
            .data(this.data.links)
            .enter()
            .append('line')
            .attr('class', 'fg-net-link')
            .attr('stroke', '#999999')
            .attr('stroke-width', function(d, i) { return d.value; })
            .attr('x1', function(d){ return fg_netplt.x_scale(Math.cos(fg_netplt.i2r(fg_netplt.node2idx[d.source]))); })
            .attr('x2', function(d){ return fg_netplt.x_scale(Math.cos(fg_netplt.i2r(fg_netplt.node2idx[d.target]))); })
            .attr('y1', function(d){ return fg_netplt.y_scale(Math.sin(fg_netplt.i2r(fg_netplt.node2idx[d.source]))); })
            .attr('y2', function(d){ return fg_netplt.y_scale(Math.sin(fg_netplt.i2r(fg_netplt.node2idx[d.target]))); })
            .append('title')
            .text(function(d) {
                return d.source + ' <-- ' + d.value + ' --> ' + d.target;
            });

        // draw new nodes
        var nodes = this.svg.selectAll(".fg-net-node")
            .data(this.data.nodes)
            .enter()
            .append('g')
            .attr('class', function(d, i) {
                return 'fg-net-node-item ' + 'node-' + d.name;
            })
            .attr('transform', function(d, i) {
                return 'translate(' + fg_netplt.x_scale(Math.cos(fg_netplt.i2r(i))) + ', '+
                                      fg_netplt.y_scale(Math.sin(fg_netplt.i2r(i))) + ')';
            })
            .on('click', function(d, i) {
                d3.select(this).classed('selected', function() { 
                    return !this.classList.contains("selected"); 
                })
            });
        nodes.append('circle')
            .attr('class', 'fg-net-node')
            .attr('r', function(d, i) { return 5 + d.value; })
            .style('fill', function(d) { return 'orange'; })
        
        // draw the text
        nodes.append('text')
            .attr('x', function(d, i) { return 5; })
            .attr('y', function(d, i) { return 5; })
            .attr('class', 'fg-net-node-text')
            .attr('title', function(d, i) { return d.value + ' Studies'; })
            .on('mouseover', this.tip.show)
            .on('mouseout', this.tip.hide)
            .text(function(d, i) { return d.name; });

        // with d3-tip plugin, we can show some message when hovering
        // if (d3.hasOwnProperty('tip')) {
        // }

    },

    i2r: function(i) {
        return 2 * Math.PI * i / this.n_nodes;
    },
}
