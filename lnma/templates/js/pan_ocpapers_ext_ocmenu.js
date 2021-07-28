/**
 * This is a plugin / extension for the pan_ocpapers.
 * 
 * Before using, please import / define the pan_ocpapers
 */

// Extend the vpp data
Object.assign(pan_ocpapers.vpp_data, {
    // the extract dict must be ready?
    
});


// Extend the vpp methods
Object.assign(pan_ocpapers.vpp_methods, {
    

});


// Extend the pan_ocpapers methods
Object.assign(pan_ocpapers, {

    /**
     * Show the outcomes menu
     */
     show_ocs_menu: function() {
        var top = 40;
        var left = 90;
        $("#pan_ocpapers_ocs_menu").css({
            position: 'absolute',
            display: "block",
            top: top,
            left: left
        }).addClass("show").menu();

        $("#pan_ocpapers_ocs_menu").menu('refresh');

        $('#pan_ocpapers_ocs_menu .ui-menu-item').on('click', function() {
            $("#pan_ocpapers_ocs_menu").hide();
        });
    },

    /**
     * Update the outcome menu
     * 
     * The input `extract_tree` should be generated before calling this
     * 
     * @param extract_tree A object for extract tree
     */
    update_ocs_menu: function(extract_tree, is_shown_itable) {
        if (typeof(is_shown_itable)=='undefined') {
            is_shown_itable = true;
        }
        // loop on the cate_attrs
        var html = [];

        // first item is the itable
        if (is_shown_itable) {
            html.push(
                '<li class="oc-menu-item">'+
                '<div onclick="pan_ocpapers.show_extract_and_papers(\''+extract_tree.itable.abbr+'\');">'+
                'Interactive Table'+
                '</div></li>'
            );
        }

        // then loop on the tree
        var oc_types = ['pwma', 'subg', 'nma']
        for (let i = 0; i < oc_types.length; i++) {
            const oc_type = oc_types[i];
            
            if (!extract_tree.hasOwnProperty(oc_type)) { continue; }

            // then, add the pwma
            html.push(
                '<li class="oc-menu-item"><div>' + 
                srv_shared._lbl(oc_type)+
                ' Outcomes</div><ul>'
            );

            // now, check groups
            var groups = Object.keys(extract_tree[oc_type].groups).sort();
            for (let j = 0; j < groups.length; j++) {
                const group = groups[j];
                
                // then, add the group
                html.push(
                    '<li class="oc-menu-item"><div>' +
                        srv_shared._lbl(group) +
                    '</div><ul>'
                );

                // now, check the cates in this group
                var cates = Object.keys(extract_tree[oc_type].groups[group].cates).sort();
                for (let k = 0; k < cates.length; k++) {
                    const cate = cates[k];
                    
                    // then, add this cate
                    html.push(
                        '<li class="oc-menu-item"><div>'+cate+'</div><ul>'
                    );

                    // now, check the ocs
                    var ocs = extract_tree[oc_type].groups[group].cates[cate].ocs;
                    var ocs_list = Object.keys(ocs).map(function(abbr) {
                        return ocs[abbr];
                    });
                    ocs_list.sort(function(a, b) {
                        return a.meta.full_name > b.meta.full_name ? 1 : -1;
                    });
                    for (let l = 0; l < ocs_list.length; l++) {
                        var ext = ocs_list[l];
                        // add this this oc
                        html.push(
                            '<li class="oc-menu-item">'+
                            '<div onclick="pan_ocpapers.show_extract_and_papers(\''+ext.abbr+'\');">'+
                            '(' + ext.n_selected + ') ' + 
                            ext.meta.full_name+
                            '</div></li>'
                        );
                    }

                    html.push('</ul></li>'); // end of the cate

                }

                html.push('</ul></li>'); // end of the group
            }

            html.push('</ul></li>'); // end of the oc_type

        }

        // put the new html into box
        $('#pan_ocpapers_ocs_menu').html(
            html.join('')
        );
    },
});