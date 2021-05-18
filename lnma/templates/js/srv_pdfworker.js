var srv_pdfworker = {
    api_url: {
        upload_pdfs: '[[ url_for("pdfworker.upload_pdfs") ]]',
        remove_pdf: '[[ url_for("pdfworker.remove_pdf") ]]',
    },
    ///////////////////////////////////////////////////////////////////////////
    // the functions related to pdf
    ///////////////////////////////////////////////////////////////////////////

    update_form_data: function(form_id, callback) {

        // get the pdf form data
        var form_data = new FormData(
            $(form_id)[0]
        );

        // send the update
        $.ajax({
            type: 'POST',
            url: srv_pdfworker.api_url.upload_pdfs,
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: callback,
            
            // 2021-05-17: add a callback for upload progress bar
            // thanks to https://stackoverflow.com/questions/15410265/file-upload-progress-bar-with-jquery
            xhr: function() {
                var xhr = new window.XMLHttpRequest();

                xhr.upload.addEventListener("progress", function(evt) {
                    if (evt.lengthComputable) {
                        var percentComplete = evt.loaded / evt.total;
                        percentComplete = parseInt(percentComplete * 100);
                        // console.log(percentComplete);

                        // show a percentage
                        $('#pdf_upload_progress').html(
                            percentComplete + '%'
                        );

                        if (percentComplete === 100) {

                        }

                    }
                }, false);

                return xhr;
            }
        });
    },

    view_pdf: function(paper_id, file_id, folder) {
        // update the toolbar
        pan_pdfviewer.update_toolbar(paper_id);

        // show the PDF panel
        pan_pdfviewer.show();

        // load the PDF
        pan_pdfviewer.load_pdf(folder, file_id);
    },

    download_pdf: function(paper_id, file_id, folder, display_name) {
        var url = '/pdfworker/download_pdf/' + folder + '/' + file_id;
        url += "?fn=" + encodeURI(display_name);
        window.open(url);
    },

    remove_pdf: function(paper_id, file_id, folder, display_name, callback) {
        var ret = window.confirm('Deleted files could NOT be recovered. Are you sure to delete [' + display_name + ']?');

        if (!ret) {
            return;
        }

        $.post(
            srv_pdfworker.api_url.remove_pdf,
            {
                paper_id: paper_id,
                pdf_metas: JSON.stringify([{
                    folder: folder,
                    file_id: file_id
                }])
            },
            callback, 
            'json'
        );
    }
};