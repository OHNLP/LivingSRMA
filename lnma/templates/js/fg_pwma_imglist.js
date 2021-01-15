var fg_pwma_imglist = {
    vpp: null,
    vpp_id: "#fg_pwma_imglist",
    headers: {
        fn_outplt1: ()=>'Analysis Result',
        fn_fnnlplt: ()=>'Analysis Result Funnel Plot',
        fn_sensplt: ()=>'Sensitivity Analysis Result',
        fn_cumuplt: ()=>'Cumulative Meta-Analysis Result'
    },

    init: function() {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                plots: [],
            },
            methods: {

                download_img: function(fn) {
                    jarvis.download_file(fn);
                },

                get_header: function(plot_id) {
                    return fg_pwma_imglist.headers[plot_id];
                }
            }
        })
    },

    draw: function(data) {
        // update the r source code file
        this.vpp.r_source = data.params.fn_rscript;
        // update the imgs
        this.vpp.plots = [];
        for (let i = 0; i < data.params.result_plots.length; i++) {
            const plot_id = data.params.result_plots[i];
            // add file name to data
            var fn = data.params[plot_id];
            this.vpp.plots.push({
                plot_id: plot_id,
                fn: fn
            });
        }
    },

    clear: function() {
        this.vpp.plots = [];
    }
}