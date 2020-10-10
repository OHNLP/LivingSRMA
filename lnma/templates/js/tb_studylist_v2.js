var tb_studylist = {
    vpp: null,
    vpp_id: '#tb-studylist',
    data: {},
    width: 400,
    all_rs: [],

    load: function() {
        // load data of these pids:
        var pids = [];
        for (var pmid in this.data.paper_dict) {
            if (this.data.paper_dict.hasOwnProperty(pmid)) {
                // console.log(this.data.paper_dict[pmid])
                if (pmid.substring(0, 6).toUpperCase() == 'NOPMID') {
                    // it is a no pmid paper, skip
                    continue;
                }
                if (!this.data.paper_dict[pmid].hasOwnProperty('title')) {
                    // the info of this paper is not yet
                    pids.push(pmid);
                }
            }
        }
        console.log('* need to load these pids', pids);
        this.get_summary_of_search_results(pids, function(dt) {
            tb_studylist.parse_summary_results(dt);
            tb_studylist.set_stage('f2');
        });
        
    },
    
    init: function(data, stage) {
        // bind data
        this.data = data;

        if (typeof(stage) == 'undefined') {
            stage = 'f2';
        }

        // init the UI
        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                total: this.all_rs.length,
                pn: 0,
                tp: 1,
                prisma: this.data.prisma,
                stage: stage,
                url: jarvis.url,
                studies: this.all_rs
            },
            methods: {
                prev_page: function() {
                    if (this.pn > 0) {
                        this.pn -= 1;
                        tb_search.search(
                            tb_search.vpp.keyword,
                            tb_search.vpp.pn * tb_search.retmax
                        );
                    }
                },

                next_page: function() {
                    if (this.pn < this.tp) {
                        this.pn += 1;
                        tb_search.search(
                            tb_search.vpp.keyword,
                            tb_search.vpp.pn * tb_search.retmax
                        );
                    }
                },

                show_study_by_pmid: function(pmid) {

                }
            }
        });
    },

    unpack: function(rows, key) {
        return rows.map(function(row) {
            return row[key];
        });
    },

    clear: function() {
        this.vpp.n = 0;
        this.vpp.headers = [];
        this.vpp.studies = [];
    },

    set_stage: function(stage) {
        // set the stage
        this.vpp.stage = stage;

        // put the papers in this stage
        var studies = [];
        for (var i = 0; i < this.data.prisma[stage].paper_list.length; i++) {
            var pmid = this.data.prisma[stage].paper_list[i];
            var paper = this.data.paper_dict[pmid];
            var ctid = paper.ctid;

            if (paper.hasOwnProperty('title')) {
                // this paper is a real PMID data or we put data in xls
                studies.push(paper);
            } else {
                studies.push(this.data.study_dict[ctid]);
            }
        }
        this.vpp.studies = studies;
        this.vpp.total = studies.length;
        console.log('* set vpp studies', studies);
    },

    set_stage_to_nct_latest: function(stage) {
        // set the stage
        this.vpp.stage = stage;

        // put the papers in this stage
        var studies = [];
        for (var i = 0; i < this.data.prisma[stage].study_list.length; i++) {
            var ctid = this.data.prisma[stage].study_list[i];
            var latest_pmid = this.data.study_dict[ctid].latest_pmid;
            var paper = this.data.paper_dict[latest_pmid];

            if (paper.hasOwnProperty('title')) {
                // this paper is a real PMID data or we put data in xls
                studies.push(paper);
            } else {
                studies.push(this.data.study_dict[ctid]);
            }
        }
        this.vpp.studies = studies;
        this.vpp.total = studies.length;
        console.log('* set vpp studies', studies);
    },

    get_summary_of_search_results: function(ids, callback) {
        $.get(
            jarvis.url.pubmed.esummary,
            {id: ids.join(',')},
            callback, 'xml'
        );
    },

    parse_summary_results: function(data) {
        var xml = $(data);
        var docsums = xml.find('DocSum');
        
        for (var i = 0; i < docsums.length; i++) {
            var docsum_xml = $(docsums[i]);

            // get PMID
            var pmid = docsum_xml.find('Id')[0].textContent;

            // get title
            var title = docsum_xml.find('Item[Name="Title"]')[0].textContent;

            // get authors
            var authors = [];
            var authors_elems = docsum_xml.find('Item[Name="Author"]');
            for (var j = 0; j < authors_elems.length; j++) {
                var elem = authors_elems[j];
                authors.push(elem.textContent);
            }

            // get journal
            var journal = docsum_xml.find('Item[Name="FullJournalName"]')[0].textContent;

            // get date
            var date = docsum_xml.find('Item[Name="PubDate"]')[0].textContent;

            // update the record
            this.data.paper_dict[pmid].title = title;
            this.data.paper_dict[pmid].date = date;
            this.data.paper_dict[pmid].journal = journal;
            this.data.paper_dict[pmid].authors = authors.join(', ');
        }
    }
}