var pan_maresults = {
    vpp_id: "#pan_maresults",
    vpp: null,
    vpp_data: {
        // flags for default plots
        has_pwma_prim_forest: false,
        has_pwma_cumu_forest: false,
        has_incd_incd_forest: false,
        has_incd_cumu_forest: false,

        // others
    },
    vpp_methods: {

    },

    init: function() {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: this.vpp_data,
            methods: this.vpp_methods,

            updated: function() {

                // draw the pwma prim
                console.log('* check has_pwma_prim_forest=' + this.has_pwma_prim_forest);
                if (this.has_pwma_prim_forest) {
                    fg_pwma_prim_forest.draw(
                        fg_pwma_prim_forest.data,
                        fg_pwma_prim_forest.cfg
                    );
                    console.log('* drawn fg_pwma_prim_forest');
                }

                // draw the pwma cumu
                console.log('* check has_pwma_cumu_forest=' + this.has_pwma_cumu_forest);
                if (this.has_pwma_cumu_forest) {
                    fg_pwma_cumu_forest.draw(
                        fg_pwma_cumu_forest.data, 
                        fg_pwma_cumu_forest.cfg
                    );
                    console.log('* drawn fg_pwma_cumu_forest');
                }

                // draw the pwma incd
                if (this.has_incd_incd_forest) {
                    console.log('* vpp draw incd forest data', fg_incd_incd_forest.data);
                    fg_incd_incd_forest.draw(
                        fg_incd_incd_forest.data, 
                        fg_incd_incd_forest.cfg
                    );
                    console.log('* drawn fg_incd_incd_forest');
                }

                // draw the incd cumu
                if (this.has_incd_cumu_forest) {
                    fg_incd_cumu_forest.draw(
                        fg_incd_cumu_forest.data, 
                        fg_incd_cumu_forest.cfg
                    );
                    console.log('* drawn fg_incd_cumu_forest');
                }

                console.log('* pan_maresults updated!');
            }
        });
    },

    clear: function() {
        // hide the plots
        this.vpp.$data.has_pwma_prim_forest = false;
        this.vpp.$data.has_pwma_cumu_forest = false;
        this.vpp.$data.has_incd_incd_forest = false;
        this.vpp.$data.has_incd_cumu_forest = false;
    },

    /**
     * Due the async of Vue.js
     * the drawing is done in the vue.updated function
     */
    show_pwma_prim_plots: function(data) {
        // draw the results
        var cfg = {
            sm: {
                name: data.params.measure_of_effect,
                sm: data.params.measure_of_effect,
            },
            mode: 'pwma_prcm',
            params: data.params
        };

        // prepare the the primary result data
        fg_pwma_prim_forest.data = data.data.primma;
        fg_pwma_prim_forest.cfg = cfg;
        
        // turn on the switch
        this.vpp.$data.has_pwma_prim_forest = true;

        // draw the cumu
        if (data.data.hasOwnProperty('cumuma')) {
            fg_pwma_cumu_forest.data = data.data.cumuma;
            fg_pwma_cumu_forest.cfg = cfg;
            this.vpp.$data.has_pwma_cumu_forest = true;
        }

        this.vpp.$forceUpdate();
    },

    show_pwma_incd_plots: function(data) {
        // draw the results of incd
        var cfg = {
            sm: {
                name: 'Event Rate',
                sm: 'Incidence (%)'
            },
            mode: 'pwma_incd'
        };

        // prepare the the primary result data
        fg_incd_incd_forest.data = data.data.incdma;
        fg_incd_incd_forest.cfg = cfg;

        console.log('* show incd forest data', fg_incd_incd_forest.data);
        
        // turn on the switch
        this.vpp.$data.has_incd_incd_forest = true;

        // draw the cumu
        if (data.data.hasOwnProperty('cumuma')) {
            fg_incd_cumu_forest.data = data.data.cumuma;
            fg_incd_cumu_forest.cfg = cfg;
            this.vpp.$data.has_incd_cumu_forest = true;
        }

        this.vpp.$forceUpdate();
    },

    resize: function() {
        var h = $(window).height() - 50;
        $(this.vpp_id).css('height', h);
    }
};