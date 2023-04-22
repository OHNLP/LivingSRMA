/**
 * This is a plugin for jarvis utils
 * 
 * Before using this plugin, make sure jarvis is already defined
 */
// Extend the jarvis with basic utils
Object.assign(jarvis, {

    // debug mode, by default is false
    debug: false,

    /**
     * Get the URL paramter value
     * @param {string} name URL paramter name
     * @returns value
     */
    get_url_paramter: function(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        var results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    },

    set_default_cq: function() {
        // set cq_abbr if not 
        if (typeof(Cookies.get('cq_abbr')) == 'undefined') {
            Cookies.set('cq_abbr', 'default');
        } else {
            console.log('* found cq_abbr=' + Cookies.get('cq_abbr') + ' in Cookies');
        }
    },

    get_link_doi: function(doi, cls) {
        if (typeof(cls) == 'undefined') {
            cls = '';
        }
        return '<a target="_blank" class="'+cls+'" href="https://doi.org/'+doi+'" title="Check the detail through DOI '+doi+'">' + doi + '</a>';
    },

    get_link_pmid: function(pmid, cls) {
        if (typeof(cls) == 'undefined') {
            cls = '';
        }
        return '<a target="_blank" href="https://pubmed.ncbi.nlm.nih.gov/'+pmid+'" title="Check the detail in PubMed '+pmid+'">' + pmid + '</a>';
    },

    get_link_nct: function(nct) {
        return '<a target="_blank" href="https://clinicaltrials.gov/ct2/show/'+nct+'" title="Check this clinical trial '+nct+'">'+nct+'</a>';
    },

    add_commas_to_number: function(x) {
        x = x.toString();
        var pattern = /(-?\d+)(\d{3})/;
        while (pattern.test(x))
            x = x.replace(pattern, "$1,$2");
        return x;
    },

    toast: function(msg, type) {
        if (typeof(type)=='undefined') {
            type = 'default';
        }
        if (typeof(toast)!='undefined') {
            toast(msg, type)
        }
    },

    copy_text_to_clipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            /* clipboard successfully set */
            console.log('* copied ' + text);
            jarvis.toast("'" + text + "' is copied to clipboard!");
        }, () => {
            /* clipboard write failed */
            console.log('* failed copy?')
        });
    }
});