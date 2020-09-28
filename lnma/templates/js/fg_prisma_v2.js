var fg_prisma = {
    vpp: null,
    vpp_id: '#fg-prisma',
    
    init: function(data) {
        this.data = data;
        // set n_ctids as number of each stage
        for (var stage in this.data.prisma) {
            this.data.prisma[stage].number = this.data.prisma[stage].n_ctids;
        }

        this.vpp = new Vue({
            el: this.vpp_id,
            data: { 
                vals: this.data.prisma 
            },
            methods: {
                fmt_num: function(x) {
                    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
                },

                update_study_list: function(stage) {
                    tb_studylist.set_stage(stage);
                },

                show_excluded_studies: function(stage) {
                    if (stage == 'e2') {
                        $( "#dialog-message-e2" ).dialog( "open" );
                    }
                },

                show_study_by_pmid: function(pmid) {

                }
            }
        });
    }
}