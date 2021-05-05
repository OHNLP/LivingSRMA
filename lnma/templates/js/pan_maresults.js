var pan_maresults = {
    vpp_id: "#pan_maresults",
    vpp: null,
    vpp_data: {
    },
    vpp_methods: {

    },

    init: function() {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: this.vpp_data,
            methods: this.vpp_methods
        });
    }
};