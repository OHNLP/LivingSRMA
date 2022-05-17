/**
 * This is a plugin for jarvis full name convertion
 * 
 * Before using this plugin, make sure jarvis is already defined
 */
// Extend the jarvis with basic utils
Object.assign(jarvis, {

    // debug, by default is false
    fullnames: {
        "DARO+D+ADT":	"Darolutamide + Docetaxel",
        "AAP+D+ADT":	"Abiraterone acetate + Docetaxel",
        "APA+ADT":	    "Apalutamide",
        "E+ADT":	    "Enzalutamide",
        "AAP+ADT":	    "Abiraterone acetate",
        "D+ADT":	    "Docetaxel",

        // for RCC
        "ATE": "Atezolizumab",
        "AXI": "Axitinib",
        "NIVO": "Nivolumab"
    },

    /**
     * Convert a name / abbr to a full name
     * @param {string} name an object's name
     * @returns string
     */
    to_fullname: function(name) {
        // to upper case 
        var _name = name.toLocaleUpperCase();

        if (this.fullnames.hasOwnProperty(_name)) {
            return this.fullnames[_name];
        } else {
            return name;
        }

    },

    /**
     * Append the fullname dictionary with given dict
     * 
     * The key / abbr will be transformed to upper case
     * for make it accepts different cases
     * 
     * @param {Object} dict a dictionary for fullnames
     * @param {boolean} overwrite overwrite exisiting value (true)
     */
    append_fullnames: function(dict, overwrite) {
        if (typeof(overwrite) == 'undefined') {
            overwrite = true;
        }
        for (const key in dict) {
            if (Object.hasOwnProperty.call(dict, key)) {
                var _key = key.toLocaleUpperCase();
                const fullname = dict[key];

                if (this.fullnames.hasOwnProperty(_key)) {
                    if (overwrite) {
                        this.fullnames[_key] = fullname;
                    }
                } else {
                    this.fullnames[_key] = fullname;
                }
            }
        }
    } 
});