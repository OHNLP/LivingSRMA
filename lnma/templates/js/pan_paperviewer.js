var pan_paperviewer = {
    vpp_id: "#pan_paperviewer",
    vpp: null,

    vpp_data: {

    },

    vpp_methods: {

    },

    init: function() {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: this.vpp_data,
            methods: this.vpp_methods,
            updated: function() {
                // resize the pan_paperviewer
                pan_paperviewer.resize();
            },
        });
    },


    resize: function() {
        // set the height for the window
        var h = $(window).height() - 100;
        $('#pan_paperviewer').css("height", h);

        $('#pan_collector_basic_info').css("height", h - 50);

        // set the height for the pdf viewer
        var h = $(window).height() - 150;
        $(this.pdfviewer_id).css('height', h + 'px');
    }
}