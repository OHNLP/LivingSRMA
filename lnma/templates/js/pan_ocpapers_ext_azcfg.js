/**
 * This is a plugin / extension for the pan_ocpapers.
 * 
 * Before using, please import / define the pan_ocpapers
 */

// Extend the vpp data
Object.assign(pan_ocpapers.vpp_data, {
    // the configurations for meta-analysis
    // make a copy from the srv_analyer
    cfgs: JSON.parse(JSON.stringify(srv_analyzer.cfgs))
});


// Extend the vpp methods
Object.assign(pan_ocpapers.vpp_methods, {
    /**
     * Decide whether to show a config or not
     * 
     * The is_used of some configs are defined by other config(s),
     * so this function helps to decide wheter to display a config or not
     * 
     * By default, the display of a config is decided by the `is_used`
     * @param {string} cfg_name 
     * @returns 
     */
    show_cfg: srv_analyzer.show_cfg,

    show_cfg_option: srv_analyzer.show_cfg_option,

    /**
     * Get the records for MA
     * 
     * For most of time, it only depends on the `extract.data`.
     * But for IO project or AE input format, it is different.
     * 
     * We need to get the correct records and apply user selection
     * to make sure the rs could be customized.
     */
    get_rs: function(grade) {
        // try to build this rs
        var rs = [];

        // first of all, we need to support the IO project analysis
        if (this.working_oc.oc_type == 'pwma' &&
            this.working_oc.meta.input_format == 'PRIM_CAT_RAW_G5') {

            if (typeof(grade) == 'undefined') {
                // use the current selected grade
                grade = this.cfgs.ae_grade.selected.toLocaleUpperCase();
            } else {
                grade = grade.toLocaleUpperCase();
            }

            // then depends on which grade is selected
            for (const pid in this.working_oc.data) {
                if (!Object.hasOwnProperty.call(this.working_oc.data, pid)) {
                    continue;   
                }

                // get this paper by a parent method
                var paper = this.get_paper_by_pid(pid);
                if (paper == null) {
                    // which means this study is not included is SR???
                    paper = {
                        authors: pid,
                        year: ''
                    }
                }

                // get some infomation
                // create a record for analyze
                // var study = this.get_first_author(paper.authors) + ' ' +
                            // this.get_year(paper.pub_date);
                var study = paper.short_name;
                var year = this.get_year(paper.pub_date);

                // get this data
                var d = this.working_oc.data[pid];

                // get data from all arms
                for (let i = 0; i < d.n_arms - 1; i++) {
                    // when i == 0, the main
                    // when i > 0, then other i-1
                    var ext = null;
                    var _study = study;
                    if (i==0) {
                        ext = d.attrs.main['g0'];
                    } else {
                        ext = d.attrs.other[i-1]['g0'];
                        _study = _study + ' CP' + (i + 1);
                    }

                    // now get data
                    var Nt = this.get_int(ext.GA_Nt);
                    var Nc = this.get_int(ext.GA_Nc);
                    var Et = this.get_int(ext[grade + '_Et']);
                    var Ec = this.get_int(ext[grade + '_Ec']);
                    var treatment = this.get_str(ext.treatment);
                    var control = this.get_str(ext.control);

                    // Now need to check the value
                    // if (this.isna(Nt) || 
                    //     this.isna(Nc) || 
                    //     this.isna(Et) ||
                    //     this.isna(Ec)) {
                        
                    //     // console.log('* skip NULL ' + " " + pid + " " + study);
                    //     continue;
                    // }
                    if (this.isna(Et)) {
                        // console.log('* skip NA ' + grade + ' Et='+Et+' ' + pid + ' ' + _study);
                        continue;
                    }
                    if (this.isna(Ec)) {
                        // console.log('* skip NA ' + grade + ' Ec='+Ec+' ' + pid + ' ' + _study);
                        continue;
                    }
                    if (this.isna(Nt)) {
                        // console.log('* skip NA ' + grade + ' Nt='+Nt+' ' + pid + ' ' + _study);
                        continue;
                    }
                    if (this.isna(Nc)) {
                        // console.log('* skip NA ' + grade + ' Nc='+Nc+' ' + pid + ' ' + _study);
                        continue;
                    }

                    if (Et == 0 && Ec == 0) {
                        console.log('* skip 0t0c ' + pid + " " + _study);
                        continue;
                    }
                    var r = {
                        // the must attributes
                        study: _study,
                        year: year,
                        Et: Et,
                        Nt: Nt,
                        Ec: Ec,
                        Nc: Nc,
                        treatment: treatment,
                        control: control,

                        // other infomation
                        grade: grade,
                        pid: pid
                    }

                    rs.push(r);
                }
            }
            return rs;
        }
    },

    get_cfg: function() {
        var cfg = srv_analyzer.get_blank_cfg();

        // copy each one
        for (const cfg_name in cfg) {
            if (!Object.hasOwnProperty.call(this.cfgs, cfg_name)) {
                continue;    
            }
            var c = this.cfgs[cfg_name];

            // put the config
            cfg[cfg_name] = c.selected;
        }

        return cfg;
    },

    analyze: function() {
        this.btn_analyze.is_disabled = false;
        jarvis.analyze();
    }
});


// Extend the pan_ocpapers methods
Object.assign(pan_ocpapers, {

});