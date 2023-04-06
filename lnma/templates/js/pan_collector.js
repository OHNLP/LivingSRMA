var pan_collector = {
    vpp_id: "#pan_collector",
    vpp: null,
    pdfviewer_id: '#ifr_pdfviewer',

    mark_keywords_as_color: function(keywords, color) {
        $('#pan_collector_basic_info').mark(
            keywords,
            { className: 'txt-' + color, separateWordSearch: false }
        );
    },

    init: function() {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                paper: null,
                show_tab: null,

                is_uploading_pdf: false,
            },
            updated: function() {
                // resize the pan_collector_basic_info
                // 2021-04-24: the abstract maybe very long
                // so make it rezie
                pan_collector.resize();
            },
            methods: {
                switch_tab: function(tab_name) {
                    this.show_tab = tab_name;
                },

                view_pdf: function(paper_id, file_id, folder) {
                    pan_collector.view_pdf(paper_id, file_id, folder);
                },

                upload_pdfs: function() {
                    this.is_uploading_pdf = true;
                    pan_collector.upload_pdfs();
                },

                download_pdf: function(paper_id, file_id, folder, display_name) {
                    srv_pdfworker.download_pdf(null, file_id, folder);
                },

                remove_pdf: function(paper_id, file_id, folder, display_name) {
                    srv_pdfworker.remove_pdf(
                        paper_id, file_id, folder, display_name,

                        function(data) {
                            console.log('* removed', data)
                            jarvis.toast('Removed PDF file successfully');

                            // update display and set to pdf tab
                            pan_collector.update(data.paper, 'pdf');
                        }
                    );
                },

                get_year: function(s) {
                    return jarvis.get_year(s);
                },

                get_first_author: function(s) {
                    return jarvis.get_first_author(s);
                },
            }
        });

        this.resize();

        // bind the context menu
        this.bind_txt_ctx_menu();
    },

    bind_txt_ctx_menu: function() {
        // $(this.vpp_id + '_basic_info').on('contextmenu', function(event) {
        $(this.vpp_id).on('contextmenu', function(event) {
            // get the highlighted text
            var text = "";
            if (window.getSelection) {
                text = window.getSelection().toString();
            } else if (document.selection && document.selection.type != "Control") {
                text = document.selection.createRange().text;
            }
            // remove the white paddings
            text = text.trim();
            console.log('* found highlighted text', text);

            // no need to show the menu when no text is selected
            if (text.length == 0) {
                return false;
            }

            // update the context menu content based on the selected attributes.
            // all of the details about this paper is need to generate the menu.
            // but since the attrs are only available in pan_ocpapers,
            // we have to use pan_oc
            pan_ocpapers.update_ctx_menu(
                text, 
                pan_collector.vpp.paper.pid
            );

            // show the context menu at where clicked
            var top = event.pageY - 20;
            var left = event.pageX;
            pan_ocpapers.show_ctx_menu(
                top, left
            );

            //blocks default Webbrowser right click menu
            return false; 
        });
        console.log('* binded ctx menu')
    },

    on_contextmenu_pdfviewer: function(event) {
        // get text
        var text = this.get_pdf_selection_text();
        
        // update the menu
        pan_ocpapers.update_ctx_menu(
            text, 
            pan_collector.vpp.$data.paper.pid
        );

        // show the context menu at where clicked
        // need to calculate the offset for the iframe
        var offset = $('#ifr_pdfviewer').offset();
        var top = offset.top + event.pageY - 20;
        var left = offset.left + event.pageX;
        
        pan_ocpapers.show_ctx_menu(
            top, left
        );
    },

    get_pdf_selection_text: function() {
        var txt = '';
        txt = document.getElementById('ifr_pdfviewer')
            .contentWindow.getSelection().toString();

        return txt;
    },

    update: function(paper, show_tab) {
        // set the default show tab to basic_info
        if (typeof(show_tab) == 'undefined') {
            show_tab = 'basic_info';
        }

        // update data
        this.vpp.paper = paper;

        // add is_pmid
        if (paper.pid_type.indexOf('MEDLINE')>=0 ||
            paper.pid_type.indexOf('PMID')>=0) {
            paper.is_pmid = true;
        }

        // update the normal UI
        this.vpp.show_tab = show_tab;
        this.vpp.$forceUpdate();

        // update the keywords highlight
        this.vpp.$nextTick(function () {
            console.log('* pan_collector UI updated');
            pan_collector.mark_keywords_as_color(
                srv_extractor.project.settings.highlight_keywords.inclusion,
                'green'
            );
        });

        // update the PDF viewer
        // this.load_pdf();
        this.resize();

        // notifiy the ocpaper to show the working paper
        pan_ocpapers.show_working_paper();
    },

    show_paper: function(pid) {
        // set loc to show
        $('#win_collector').css("right", 0);

        // resize
        pan_collector.resize();

        // get the paper
        srv_extractor.get_paper(
            pid, 
            function(data) {
                if (data.success) {
                    pan_collector.update(data.paper);
                } else {
                    toast('Error when getting paper, try later.', 'error');
                }
            }
        );
    },

    show: function() {
        $(this.vpp_id).show();
    },

    hide: function() {
        // 2023-04-06: complete the logic here
        $('#win_collector').css('right', 5000); 
    },

    view_pdf: function(paper_id, file_id, folder) {
        // update the pdf viewer size
        this.resize();

        // load the pdf
        this.load_pdf(folder, file_id);
    },

    load_pdf: function(folder, file_id) {
        var pdf_url = "/pdfworker/pdf/" + folder + "/" + file_id + '.pdf';

        // just load the blank page
        if (typeof(folder) == 'undefined') {
            pdf_url = '/pdfworker/view_pdf';
        }

        // get the highlight_keywords
        var highlight_keywords = pan_collector.get_pdf_highlight_keywords();

        // show the pdf by the 
        document.getElementById("ifr_pdfviewer")
            .contentWindow.LNMA.open_pdf(pdf_url, highlight_keywords);
    },

    /**
     * Get the keywords and color for highlighting in PDF
     */
    get_pdf_highlight_keywords: function() {
        var tmp = [];

        // first, the keywords from the project
        tmp.push({
            keywords: srv_extractor.project.settings.highlight_keywords.inclusion,
            color: 'green'
        });

        // second, push the outcome name if current is not working on itable

        // third, push the pdf highlight keywords in project settings
        tmp.push({
            keywords: srv_extractor.project.settings.pdf_keywords.main,
            color: 'yellow'
        });

        return tmp;
    },

    upload_pdfs: function() {
        // get the current working paper paper_id
        var paper_id = this.vpp.paper.paper_id;

        // call pdfworker service to upload
        srv_pdfworker.update_form_data(
            '#form_pdf_files',

            // the callback function
            function(data) {
                console.log(data);
                // enable the upload button
                pan_collector.vpp.$data.is_uploading_pdf = false;

                if (data.success) {
                    jarvis.toast('Uploaded PDF for paper!');
                    // update display and set to pdf tab
                    pan_collector.update(data.paper, 'pdf');

                } else {
                    toast('Error when uploading PDF, try later.', 'error')
                }
            }
        );
    },

    resize: function() {
        // set the height for the window
        var h = $(window).height() - 50;
        $('#pan_collector').css("height", h);

        $('#pan_collector_basic_info').css("height", h - 50);

        // set the height for the pdf viewer
        var h = $(window).height() - 150;
        $(this.pdfviewer_id).css('height', h + 'px');
    },
};

