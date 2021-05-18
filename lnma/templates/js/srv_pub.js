var srv_pub = {
    url: {
        itable: "[[ url_for('pub.itable') ]]",
    },

    goto_itable: function(prj) {
        location.href = this.url.itable + '?prj=' + prj;
    }
};