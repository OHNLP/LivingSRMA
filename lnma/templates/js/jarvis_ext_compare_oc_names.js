/**
 * This is a plugin for jarvis utils
 * 
 * Before using this plugin, make sure jarvis is already defined
 */
// Extend the jarvis with basic utils
Object.assign(jarvis, {

    // debug mode, by default is false
    oc_orders: [],

    /**
     * Compare outcome name a and b for sorting
     * @param {Object} a oc item
     * @param {Object} b oc item
     * @returns value
     */
    compare_oc_names: function(a, b) {
        var fn_a = a.oc_full_name.toLocaleLowerCase();
        var fn_b = b.oc_full_name.toLocaleLowerCase();
        var loc_a = jarvis.oc_orders.indexOf(fn_a);
        var loc_b = jarvis.oc_orders.indexOf(fn_b);
        var ret = 0;
        var flag = 0;
            
        if (loc_a>=0) {
            if (loc_b>=0) {
                ret = loc_a - loc_b;
                flag = 3;

            } else {
                ret = -1;
                flag = 2;
            }
        } else if (loc_b>=0) {
            ret = 1;
            flag = 1;

        } else {
            // just compare these two
            ret = a.oc_full_name.localeCompare(b.oc_full_name);
        }

        // console.log(
        //     '* compare['+flag+']:',
        //     ret, '=', 
        //     fn_a, '<=>',
        //     fn_b
        // );

        return ret;
    },
});