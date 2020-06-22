var fm_loader = {
    box: null,
    box_id: '#fm_loader',
    vpp: null,
    vpp_id: '#fm_loader',
    data: null,

    init: function() {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                btn_upload: {
                    disabled: false,
                    txt_normal: 'Upload',
                    txt_working: 'Uploading ...'
                },

                dataset_summary: '',

                datasets: []
            },
            methods: {
                upload: function() {
                    fm_loader.upload_data_file();
                }
            }
        });
    },

    toggle_btn_upload: function() {
        this.vpp.btn_upload.disabled = !this.vpp.btn_upload.disabled;
    },

    set_dataset_summary: function(s) {
        this.vpp.dataset_summary = s;
    },

    upload_data_file: function() {
        if ($('#ipt-csv-file').val() == '') {
            // msger.show('Choose a Data File for analysis', msger.WARNING);
            return;
        }
        // update UI
        this.vpp.btn_upload.disabled = true;
        var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: './read_file',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                console.log(data);
                fm_loader.toggle_btn_upload();
                jarvis.on_read_data_file(data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error(textStatus, errorThrown);
            }
        });
    },
}