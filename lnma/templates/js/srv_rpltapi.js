var srv_rpltapi = {
    {% if config['is_local'] %}
    url: {
        pwma_prcm: "[[ url_for('rplt.pwma_prcm') ]]",
        pwma_incd: "[[ url_for('rplt.pwma_incd') ]]",
    },
    {% else %}
    url: {
        pwma_prcm: "https://rplt.living-evidence.com/rplt/PWMA_PRCM",
        pwma_incd: "https://rplt.living-evidence.com/rplt/PWMA_INCD",
    },
    {% endif %}

    analyze_pwma_prcm: function(params, callback) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: this.url.pwma_prcm,
            data: params,
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                console.error(textStatus, errorThrown);
            }
        });
    },

    analyze_pwma_incd: function(params, callback) {
        $.ajax({
            type: 'POST',
            dataType: 'json',
            url: this.url.pwma_prcm,
            data: params,
            cache: false,
            success: callback,
            error: function(jqXHR, textStatus, errorThrown) {
                console.error(textStatus, errorThrown);
            }
        });
    } 
};