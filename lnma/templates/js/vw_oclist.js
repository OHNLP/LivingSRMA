var vw_oclist = {
    vpp: null,
    vpp_id: '#vw_oclist',
    select_mode: 'checkbox', // radio, checkbox
    pids: [],

    init: function(data) {
        // bind local data
        this.data = data;

        // init local db
        alasql('create table aes');
        alasql('select * into aes from ?', [this.data.rs])
        
        this.rs = {},
        this.rs_stat = {
            cnt_cates: 0,
            cnt_aes: 0,
        };
        
        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                rs: this.rs,
                select_mode: this.select_mode,
                rs_stat: this.rs_stat
            },
            methods: {
                toggle_ae: function(event) {
                    var ae_cate = event.target.getAttribute('ae_cate');
                    var ae_name = event.target.getAttribute('ae_name');
                    var ae_grade = event.target.getAttribute('ae_grade');

                    // add effect
                    if (this.select_mode == 'checkbox') {
                        $(event.target).toggleClass('oc-type-selected');
                    } else {
                        $('.oc-type').removeClass('oc-type-selected');
                        $(event.target).addClass('oc-type-selected');
                    }

                    // call the worker to update everything related
                    // jarvis will do this task accordingly
                    jarvis.toggle_ae(ae_cate, ae_name, ae_grade);
                },

                get_grade_label: function(g) {
                    return jarvis.texts[g];
                },

                toggle_cate: function(cate) {
                    this.rs[cate].is_close = !this.rs[cate].is_close;
                },

                toggle_all_cates: function(flag) {
                    for (var key in this.rs) {
                        this.rs[key].is_close = flag;
                    }
                },

                clear: function() {
                    $('.oc-type').removeClass('oc-type-selected');
                    jarvis.clear_all_ae();
                }
            }
        });

        this.update([]);
    },

    get_pid_condition: function() {
        if (this.pids.length == 0) {
            return 'pid is not null ';
        } else {
            var cond = this.pids.map(function(v) { return '' + v}).join(',');
            return 'pid in (' + cond + ') '
        }
    },
    

    update: function(pids) {
        // update the pid
        this.pids = pids;
        var sql = 'select ae_cate, ae_name, ' +
            '  count(case when has_GA = true then pid else null end) as cnt_ga, ' +
            '  count(case when has_G3H = true then pid else null end) as cnt_g3h, ' +
            '  count(case when has_G5N = true then pid else null end) as cnt_g5n ' +
            'from aes ' + 
            'where ' +
            this.get_pid_condition() + ' ' + 
            'group by ae_cate, ae_name ' + 
            'order by ae_cate asc, ae_name asc';
        console.log(sql);
        // init the result
        var raw_rs = alasql(sql);
        var rs = {};
        var rs_stat = {
            cnt_cates: 0,
            cnt_aes: 0,
        };
        for (var i = 0; i < raw_rs.length; i++) {
            var r = raw_rs[i];
            if (rs.hasOwnProperty(r.ae_cate)) {
                //
            } else {
                rs[r.ae_cate] = {
                    ae_cate: r.ae_cate,
                    is_close: false,
                    aes: []
                }
                rs_stat.cnt_cates += 1;
            }
            // put this ae into cate
            rs[r.ae_cate]['aes'].push({
                ae_name: r.ae_name,
                cnt_ga: r.cnt_ga,
                cnt_g3h: r.cnt_g3h,
                cnt_g5n: r.cnt_g5n
            });
            rs_stat.cnt_aes += 1;
        }
        // bind results 
        this.raw_rs = raw_rs;
        this.rs = rs;
        this.rs_stat = rs_stat;

        // update vpp data
        this.vpp.rs = this.rs;
        this.vpp.rs_stat = this.rs_stat;

        // update tips
        $(document).tooltip({
            position: {
                my: "left top",
                at: "right+5 top-5",
                collision: "none"
            }
        });
    },

    toggle_ae: function(ae_cate, ae_name, ae_grade) {

    }
};