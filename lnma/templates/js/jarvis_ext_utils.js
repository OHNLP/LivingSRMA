/**
 * This is a plugin for jarvis utils
 * 
 * Before using this plugin, make sure jarvis is already defined
 */
// Extend the jarvis with basic utils
Object.assign(jarvis, {

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
    }
});