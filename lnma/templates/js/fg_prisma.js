var fg_prisma = {
    vpp: null,
    vpp_id: '#fg-prisma',
    
    init: function(data) {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: { vals: data },
            methods: {
                fmt_num: function(x) {
                    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                },

                update_study_list: function(stage) {
                    tb_studylist.update_study_list(stage);
                },

                show_excluded_studies: function(stage) {
                    if (stage.stage == 'e2') {
                        $( "#dialog-message-e2" ).dialog( "open" );
                    }
                },

                show_study_by_pmid: function(pmid) {

                }
            }
        });
    },

    draw: function(data) {
        this.vpp.vals = data.vals;
    },

    draw_only_number: function(data) {
        for (var key in data.vals) {
            if (data.vals.hasOwnProperty(key)) {
                var element = data.vals[key];
                this.vpp.vals[key].number = element.number;
            }
        }
    }
}