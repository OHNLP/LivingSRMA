var fg_prisma = {
    vpp: null,
    vpp_id: '#fg-prisma',
    
    sample: {

        vals: {
            b1: { stage: 'b1', number: 5043, text: 'Records retrieved from database search' },
            b2: { stage: 'b2', number: 0, text: 'Records identified through other sources' },
            b3: { stage: 'b3', number: 4983, text: 'Records after removing dupicates' },
            b4: { stage: 'b4', number: 4938, text: 'Records initialized screened' },
            b5: { stage: 'b5', number: 72, text: 'Full-text articles assessed for eligibility' },
            b6: { stage: 'b6', number: 12, text: 'Studies included in systematic review' },
            b7: { stage: 'b7', number: 9, text: 'Studies included in meta-analysis' },
            e1: { stage: 'e1', number: 4911, text: 'Excluded by title and abstract review' },
            e2: { stage: 'e2', number: 60, text: 'Excluded by full text review' },
            e3: { stage: 'e3', number: 3, text: 'Studies not included by in meta-analysis' },
            a1: { stage: 'a1', number: 2, text: 'Records identified through automated search' },
            a2: { stage: 'a2', number: 1, text: 'New studies included in systematic review' },
            a3: { stage: 'a3', number: 1, text: 'New studies included in meta-analysis' },
            u1: { stage: 'u1', number: 1, text: 'Updated studies in SR' },
            u2: { stage: 'u2', number: 1, text: 'Updated studies in MA' },
            f1: { stage: 'f1', number: 13, text: 'Final number in qualitative synthesis (systematic review)' },
            f2: { stage: 'f2', number: 10, text: 'Final number in quantitative synthesis (meta-analysis)' }
        }
    },
    
    init: function() {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: this.sample,
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
                }
            }
        });
    },

    draw: function(data) {
        this.vpp.vals = data.vals;
    },

    draw_only_number: function(data) {
        for (const key in data.vals) {
            if (data.vals.hasOwnProperty(key)) {
                const element = data.vals[key];
                this.vpp.vals[key].number = element.number;
            }
        }
    }
}