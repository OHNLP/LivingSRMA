var fg_frsplt = {
    box: null,
    box_id: '#fg-nma-frsplt',
    svg: null,
    svg_id: '#fg-nma-frsplt-svg',
    data: null,
    width: 450,
    height: 300,
    line_height: 20,
    line_text_padding_top: 5,
    top_y: 15,
    base_y: 60,
    col1_base_x: 0,
    col2_base_x: 80,
    col3_base_x: 310,
    col4_base_x: 360,
    dot_r: 2, 

    sample: {
        title: 'Comparison vs "plac"',
        subtitle: 'Fixed Effect Model',
        sm: 'HR',
        val_min: -1.23,
        val_max: -0.42,
        glb_min: -1.56,
        glb_max: -0.01,
        vals: [
            {treatment: 'acar', val: -0.83, lower: -1.04, upper: -0.61},
            {treatment: 'benf', val: -0.73, lower: -1.29, upper: -0.17},
            {treatment: 'metf', val: -1.13, lower: -1.43, upper: -0.82},
            {treatment: 'migl', val: -0.95, lower: -1.48, upper: -0.50},
            {treatment: 'piog', val: -1.13, lower: -1.56, upper: -0.70},
            {treatment: 'rosi', val: -1.23, lower: -1.48, upper: -0.98},
            {treatment: 'sita', val: -0.57, lower: -1.26, upper: -0.12},
            {treatment: 'sulf', val: -0.42, lower: -0.89, upper: -0.06},
            {treatment: 'vild', val: -0.70, lower: -1.39, upper: -0.01}
        ]
    },

    init: function() {
        this.box = $(this.box_id)
            .css('width', this.width);

        this.svg = d3.select(this.svg_id)
            .attr('width', this.width)
            .attr('height', this.height);

        this.base_y = this.top_y + this.line_height * 3;
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
        // clear existing figure
        this.svg.selectAll("*").remove();

        // resize the svg height
        var new_height = (data.vals.length + 2) * this.line_height + this.base_y;
        this.svg.attr('height', new_height);

        // update x_scale
        var x_min = data.glb_min > 1 ? 0.5: data.glb_min;
        var x_max = data.glb_max < 1 ? 1.5: data.glb_max;
        this.x_scale = d3.scaleLinear()
            .domain([x_min, x_max])
            .range([this.col2_base_x, this.col3_base_x]);

        // update the size_scale
        this.size_scale = d3.scaleLinear()
            .domain([data.val_min, data.val_max])
            .range([5, 10]);

        // draw the title
        var txts = [
            [data.title, 'fg-title',       this.col1_base_x, this.top_y],
            [data.subtitle, 'fg-subtitle', this.col1_base_x, this.top_y + this.line_height * 0.9],
            ['Treatment', 'fg-frs-th fg-frs-col1', this.col1_base_x, this.top_y + this.line_height * 2.2],
            ['', 'fg-frs-th fg-frs-col2', this.col2_base_x, this.top_y + this.line_height * 2.2],
            [data.sm.toLocaleUpperCase(), 'fg-frs-th fg-frs-col3', this.col3_base_x, this.top_y + this.line_height * 2.2],
            ['95% - CI', 'fg-frs-th fg-frs-col4', this.col4_base_x, this.top_y + this.line_height * 2.2]
        ]
        for (let i = 0; i < txts.length; i++) {
            const t = txts[i];
            this.svg.append('text').attr('class', t[1])
                .attr('x', t[2]).attr('y', t[3])
                .text(t[0]);
        }

        // draw each line
        var lines = this.svg.selectAll('.fg-frs-item')
            .data(data.vals)
            .enter()
            .append('g')
            .attr('class', function(d, i) {
                return 'fg-frs-item ' + 'frs-' + d.treatment;
            })
            .attr('transform', function(d, i) {
                var t = 'translate(0, ' + (fg_frsplt.base_y + i * fg_frsplt.line_height) + ')';
                return t;
            });
        // draw each line - bg
        // lines.append('rect')
        //     .attr('class', 'fg-row-bg')
        //     .attr('x', 0)
        //     .attr('y', - this.line_height / 2)
        //     .attr('width', this.width)
        //     .attr('height', this.line_height);

        // draw each line - column 1 - treatment
        lines.append('text')
            .attr('class', 'fg-frs-treat')
            .attr('x', this.col1_base_x)
            .attr('y', this.line_text_padding_top)
            .text(d => d.treatment);

        // draw each line - column 2 - something like the box plot
        lines.append('line')
            .attr('class', 'fg-frs-line')
            .attr('x1', d => fg_frsplt.x_scale(d.lower))
            .attr('x2', d => fg_frsplt.x_scale(d.upper))
            .attr('y1', 0)
            .attr('y2', 0);

        lines.append('rect')
            .attr('class', 'fg-frs-box')
            .attr('x', d => fg_frsplt.x_scale(d.val) - fg_frsplt.size_scale(Math.abs(d.val)) / 2)
            .attr('y', d => 0 - fg_frsplt.size_scale(Math.abs(d.val)) / 2)
            .attr('width', d => fg_frsplt.size_scale(Math.abs(d.val)))
            .attr('height', d => fg_frsplt.size_scale(Math.abs(d.val)));
        
        lines.append('circle')
            .attr('class', 'fg-frs-mddot')
            .attr('cx', d => fg_frsplt.x_scale(d.val))
            .attr('cy', 0)
            .attr('r', this.dot_r);

        // draw each line - column 3 - Value (MD/RR/HR/OR)
        lines.append('text')
            .attr('x', this.col3_base_x)
            .attr('y', this.line_text_padding_top)
            .text(d => d.val.toFixed(2));
        
        // draw each line - column 4 - 95% -CI
        lines.append('text')
            .attr('x', this.col4_base_x)
            .attr('y', this.line_text_padding_top)
            .text(d => '[' + d.lower.toFixed(2) + '; ' + d.upper.toFixed(2) + ']');

        // draw vert guideline
        this.svg.append('line')
            .attr('class', 'fg-frs-guideline')
            .attr('x1', d => fg_frsplt.x_scale(1))
            .attr('x2', d => fg_frsplt.x_scale(1))
            .attr('y1', this.base_y - this.line_height)
            .attr('y2', this.base_y + this.line_height * data.vals.length);

        // draw the axis
        this.axis = d3.axisBottom(this.x_scale).ticks(7);
        this.svg.append('g')
            .attr('transform', 'translate(' + 0 + ', ' + 
                (this.base_y + this.line_height * data.vals.length) + ')')
            .call(this.axis);
    }
}