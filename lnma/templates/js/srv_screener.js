var srv_screener = {

    api_url: {
        get_stat: '[[ url_for("screener.get_stat") ]]',
        get_paper_by_id: '[[ url_for("screener.get_paper_by_id") ]]',
        get_papers_by_stage: '[[ url_for("screener.get_papers_by_stage") ]]',

        // for screening
        set_unscreened: '[[ url_for("screener.sspr_set_papers_unscreened") ]]',
        set_needchkft: '[[ url_for("screener.sspr_set_papers_needchkft") ]]',
        exclude_ta: '[[ url_for("screener.sspr_exclude_papers_ta") ]]',
        exclude_tt: '[[ url_for("screener.sspr_exclude_papers_tt") ]]',
        exclude_ab: '[[ url_for("screener.sspr_exclude_papers_ab") ]]',
        exclude_ft: '[[ url_for("screener.sspr_exclude_papers_ft") ]]',
        include_sr: '[[ url_for("screener.sspr_include_papers_sr") ]]',
        include_srma: '[[ url_for("screener.sspr_include_papers_srma") ]]',

        // for labeling 
        set_label_ckl: '[[ url_for("screener.sspr_set_label_ckl") ]]',
        unset_label_ckl: '[[ url_for("screener.sspr_unset_label_ckl") ]]',
        set_rct_feedback: '[[ url_for("screener.sspr_set_rct_feedback") ]]',

        // for NCT8
        set_rct_id: '[[ url_for("screener.set_rct_id") ]]',

        // for PMID
        set_pmid: '[[ url_for("screener.set_pmid") ]]',

        // for PMID
        set_pub_date: '[[ url_for("screener.set_pub_date") ]]',

        // for tag
        add_tag: '[[ url_for("screener.add_tag") ]]',
        toggle_tag: '[[ url_for("screener.toggle_tag") ]]'
    },

    project: {},

    stage: {
        // view stage
        all_of_them: { title: 'All References' },
        decided: { title: 'Decided References' },

        // main stages
        unscreened: { title: 'Unscreened References' },
        passed_title_not_fulltext: { title: 'Full-text review' },
        excluded_by_title: { title: 'Excluded after checking title' },
        excluded_by_abstract: { title: 'Excluded after checking abstract' },
        excluded_by_fulltext: { title: 'Excluded after checking fulltext' },
        included_sr: { title: 'Included in SR' },
        included_srma: { title: 'Included in Both SR and MA' },
        
        // extended stages
        included_only_sr: { title: 'Included only in SR' },
        excluded_by_title_abstract: { title: 'Excluded after checking title and abstract' },
        excluded_by_rct_classifier: { title: 'Excluded by RCT classifier' },
    },

    // current stages
    STAGE_UNSCREENED: 'unscreened',
    STAGE_EXCLUDED_BY_TITLE: 'excluded_by_title',
    STAGE_EXCLUDED_BY_ABSTRACT: 'excluded_by_abstract',
    STAGE_EXCLUDED_BY_FULLTEXT: 'excluded_by_fulltext',
    STAGE_INCLUDED_SR: 'included_sr',
    STAGE_INCLUDED_SRMA: 'included_srma',
    
    // Not used stages
    // STAGE_INCLUDED_ONLY_SR: 'included_only_sr',
    STAGE_EXCLUDED_BY_TITLE_ABSTRACT: 'excluded_by_title_abstract',
    STAGE_EXCLUDED_BY_RCT_CLASSIFIER: 'excluded_by_rct_classifier',

    // just for display purpose, not a real stage
    STAGE_ALL_OF_THEM: 'all_of_them',
    STAGE_DECIDED: 'decided',
    STAGE_UNKNOWN: 'unknown',

    // attribute name for the user feedback
    ATTR_PRED_RCT_USR_FB: 'usr_fb',
    RCT_USER_FEEDBACK: {
        '0': '<b class="text-danger">NOT RCT</b>',
        '1': '<b class="text-success"><i class="fa fa-bong"></i> RCT</b>',
        '': '?'
    },

    // stage states
    ss: {
        rs: {
            e1:  { name: 'Duplicate record(s)', color: 'grey' },
            e2:  { name: 'Excluded by title', color: 'grey' },
            e21: { name: 'Excluded by RCT classifier', color: 'grey' },
            e22: { name: 'Excluded by abstract', color: 'grey' },
            e3:  { name: 'Excluded by full-text review', color: 'grey' },
            e4:  { name: 'Excluded due to study update', color: 'grey' },

            f1:  { name: 'Included in SR', color: '#007bff' },
            f3:  { name: 'Included in SR and MA', color: 'green' },

            na:  { name: 'Not decided', color: 'white' }
        }
    },

    get_stage: function(paper) {
        if (paper.ss_rs == 'na' && paper.ss_pr == 'na') {
            return this.STAGE_UNSCREENED;
        } else if (paper.ss_rs == 'f1') {
            return this.STAGE_INCLUDED_SR;
        } else if (paper.ss_rs == 'f3') {
            return this.STAGE_INCLUDED_SRMA;
        } else if (paper.ss_rs == 'e2') {
            return this.STAGE_EXCLUDED_BY_TITLE;
        } else if (paper.ss_rs == 'e22') {
            return this.STAGE_EXCLUDED_BY_ABSTRACT;
        } else if (paper.ss_rs == 'e3') {
            return this.STAGE_EXCLUDED_BY_FULLTEXT;
        } else {
            return this.STAGE_UNKNOWN;
        }
    },

    get_stat: function(callback) {
        var url = this.api_url.get_stat;
        var project_id = Cookies.get('project_id');

        $.get(
            url,
            {project_id: project_id, ver: Math.random()},
            callback, 
            'json'
        );
    },

    get_paper_by_id: function(paper_id, callback) {
        var project_id = Cookies.get('project_id');
        var url = this.api_url.get_paper_by_id;

        $.get(
            url,
            {project_id: project_id, paper_id: paper_id},
            callback, 
            'json'
        );
    },

    get_papers: function(stage, callback) {
        var project_id = Cookies.get('project_id');
        var url = this.api_url.get_papers_by_stage;

        $.get(
            url,
            {project_id: project_id, stage: stage},
            callback, 
            'json'
        );
    },

    ///////////////////////////////////////////////////////////////////////////
    // the functions related to screening
    ///////////////////////////////////////////////////////////////////////////

    set_rct_id: function(paper_id, rct_id, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        
        var url = this.api_url.set_rct_id;
        $.post(
            url,
            {
                project_id: project_id, 
                paper_id: paper_id, 
                rct_id: rct_id
            },
            callback,
            'json'
        );  

    },

    set_pmid: function(paper_id, pmid, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        
        var url = this.api_url.set_pmid;
        $.post(
            url,
            {
                project_id: project_id, 
                paper_id: paper_id, 
                pmid: pmid
            },
            callback,
            'json'
        );  

    },

    set_pub_date: function(paper_id, pub_date, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        
        var url = this.api_url.set_pub_date;
        $.post(
            url,
            {
                project_id: project_id, 
                paper_id: paper_id, 
                pub_date: pub_date
            },
            callback,
            'json'
        );  

    },

    add_tag: function(paper_id, tag, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        
        var url = this.api_url.add_tag;
        $.post(
            url,
            {paper_id: paper_id, tag: tag},
            callback,
            'json'
        );  
    },

    toggle_tag: function(paper_id, tag, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        
        var url = this.api_url.toggle_tag;
        $.post(
            url,
            {paper_id: paper_id, tag: tag},
            callback,
            'json'
        );  
    },

    set_unscreened: function(paper_id, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        var paper_ids = [paper_id].join(',');
        
        var url = this.api_url.set_unscreened;
        $.post(
            url,
            {paper_ids: paper_ids, project_id: project_id},
            callback,
            'json'
        );
    },

    set_needchkft: function(paper_id, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        var paper_ids = [paper_id].join(',');
        
        var url = this.api_url.set_needchkft;
        $.post(
            url,
            {paper_ids: paper_ids, project_id: project_id},
            callback,
            'json'
        );
    },

    exclude_by_tt: function(paper_id, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        var paper_ids = [paper_id].join(',');
        
        var url = this.api_url.exclude_tt;
        $.post(
            url,
            {paper_ids: paper_ids, project_id: project_id},
            callback,
            'json'
        );
    },

    exclude_by_ab: function(paper_id, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        var paper_ids = [paper_id].join(',');
        
        var url = this.api_url.exclude_ab;
        $.post(
            url,
            {paper_ids: paper_ids, project_id: project_id},
            callback,
            'json'
        );
    },

    exclude_by_ft: function(paper_id, reason, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        var paper_ids = [paper_id].join(',');
        
        var url = this.api_url.exclude_ft;
        $.post(
            url,
            {paper_ids: paper_ids, project_id: project_id, reason: reason},
            callback,
            'json'
        );
    },

    include_in_sr: function(paper_id, reason, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        var paper_ids = [paper_id].join(',');
        
        var url = this.api_url.include_sr;
        $.post(
            url,
            {paper_ids: paper_ids, project_id: project_id, reason: reason},
            callback,
            'json'
        );
    },

    include_in_srma: function(paper_id, callback) {
        // send request to backend
        var project_id = Cookies.get('project_id');
        var paper_ids = [paper_id].join(',');
        
        var url = this.api_url.include_srma;
        $.post(
            url,
            {paper_ids: paper_ids, project_id: project_id},
            callback,
            'json'
        );
    },
    
    set_label_check_later: function(paper_id, callback) {
        // send request
        var project_id = Cookies.get('project_id');
        var paper_ids = [paper_id].join(',');
        
        var url = this.api_url.set_label_ckl;
        $.post(
            url,
            {paper_ids: paper_ids, project_id: project_id},
            callback,
            'json'
        );
    },
    
    unset_label_check_later: function(paper_id, callback) {
        // send request
        var project_id = Cookies.get('project_id');
        var paper_ids = [paper_id].join(',');
        
        var url = this.api_url.unset_label_ckl;
        $.post(
            url,
            {paper_ids: paper_ids, project_id: project_id},
            callback,
            'json'
        );
    },
    
    set_rct_feedback: function(paper_id, feedback, callback) {
        // send request
        var project_id = Cookies.get('project_id');
        var paper_ids = [paper_id].join(',');
        
        var url = this.api_url.set_rct_feedback;
        $.post(
            url,
            {paper_ids: paper_ids, project_id: project_id, feedback: feedback},
            callback,
            'json'
        );
    },

    has_label_ckl: function(d) {
        if (d.ss_ex.hasOwnProperty('label')) {
            if (d.ss_ex.label.hasOwnProperty('CKL')) {
                return true;
            }
        }
        return false;
    }
};