var srv_analyzer = {
    
    // all urls for analyzer
    url: {
        azoc: "[[ url_for('analyzer.azoc') ]]",

        get_paper: "[[ url_for('analyzer.get_paper') ]]",
        get_extract: "[[ url_for('analyzer.get_extract') ]]",
        get_extracts: "[[ url_for('analyzer.get_extracts') ]]",
        get_extract_and_papers: "[[ url_for('analyzer.get_extract_and_papers') ]]",
    },

    // the project information
    projct: null,


    get_paper: function(pid, callback) {
        $.ajax({
            type: 'GET',
            dataType: "json",
            url: this.url.get_paper,
            data: {
                pid: pid,
                rnd: Math.random(),
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when getting included papers', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },

    get_extracts: function(project_id, callback) {
        $.get(
            this.url.get_extracts,
            {
                project_id: project_id,
                rnd: Math.random()
            },
            callback,
            'json'
        );
    },

    get_extracts: function(project_id, callback) {
        $.get(
            this.url.get_extracts,
            {
                project_id: project_id,
                rnd: Math.random()
            },
            callback,
            'json'
        );
    },

    get_extract_and_papers: function(project_id, abbr, callback) {
        $.ajax({
            type: 'GET',
            dataType: "json",
            url: this.url.get_extract_and_papers,
            data: {
                project_id: project_id,
                abbr: abbr,
                rnd: Math.random()
            },
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                jarvis.toast('Something wrong when getting included papers', 'alert');
                console.error(textStatus, errorThrown);
            }
        });
    },
};