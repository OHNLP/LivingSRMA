/**
 * This is a plugin for jarvis utils
 * 
 * Before using this plugin, make sure jarvis is already defined
 */
// Extend the jarvis with basic utils
Object.assign(jarvis, {
    // sort by given list
    sort_by_list: function(vs, list, reverse) {
        if (typeof(list) == 'undefined') {
            list = [];
        }
        if (typeof(reverse) == 'undefined') {
            reverse = false;
        }
        var _list = list.map(function(v) {
            return v.toLocaleLowerCase();
        });
        vs.sort((function(orders, is_reverse){
            return function(a, b) {
                var fn_a = a.toLocaleLowerCase();
                var fn_b = b.toLocaleLowerCase();

                var loc_a = orders.indexOf(fn_a);
                var loc_b = orders.indexOf(fn_b);
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
                    ret = fn_a.localeCompare(fn_b);
                }

                if (reverse) {
                    return -1 * ret;
                } else {
                    return ret;
                }
            }
        })(_list, reverse));

        return vs;
    },

    // debug mode, by default is false
    oc_orders: [],

    /**
     * Compare outcome name a and b for sorting
     * @param {Object} a oc item
     * @param {Object} b oc item
     * @returns value
     */
    compare_oc_names: function(a, b) {
        var fn_attr = '';
        var fn_a = null;
        var fn_b = null;
        if (a.hasOwnProperty('oc_fullname')) {
            fn_attr = 'oc_fullname';
            fn_a = a[fn_attr].toLocaleLowerCase();
            fn_b = b[fn_attr].toLocaleLowerCase();

        } else if (a.hasOwnProperty('oc_full_name')) {
            fn_attr = 'oc_full_name';
            fn_a = a[fn_attr].toLocaleLowerCase();
            fn_b = b[fn_attr].toLocaleLowerCase();

        } else if (typeof(a) == 'string'){
            // for simple case, just sort the name
            fn_a = a.toLocaleLowerCase();
            fn_b = b.toLocaleLowerCase();

        } else {
            fn_a = '';
            fn_b = '';
        }

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
            ret = fn_a.localeCompare(fn_b);
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