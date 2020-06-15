var tb_studylist = {
    vpp: null,
    vpp_id: '#tb-studylist',
    data: {},
    width: 400,
    
    all_rs: [],

    load: function(data) {
        this.prisma = data.prisma;
        this.all_rs = data.studylist;
        // load data of these pmids:
        var pmids = [];
        for (let i = 0; i < data.studylist.length; i++) {
            var item = data.studylist[i];
            if (item.pid_type == 'pmid') {
                pmids.push(item.pmid);
            }
        }
        // var pmids = this.unpack(this.all_rs.slice(0, 11), 'pmid');
        this.get_summary_of_search_results(pmids, function(dt) {
            tb_studylist.parse_summary_results(dt);
            tb_studylist.init();
            tb_studylist.update_study_list({stage:'f2'});
        });
        
    },
    
    init: function() {
        this.vpp = new Vue({
            el: this.vpp_id,
            data: {
                total: this.all_rs.length,
                pn: 0,
                tp: 1,
                stage: {text: 'Final number in qualitative synthesis', number: this.all_rs.length},
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

    set_stage: function(stage, studies) {
        this.vpp.stage = stage;
        this.vpp.studies = studies;
    },

    get_summary_of_search_results: function(ids, callback) {
        $.get(
            jarvis.url.pubmed.esummary,
            {id: ids.join(',')},
            callback, 'xml'
        );
    },

    update_study_list: function(stage) {
        this.vpp.stage = this.prisma[stage.stage];
        // filter the studies
        var studies = [];
        for (let i = 0; i < this.all_rs.length; i++) {
            var study = this.all_rs[i];
            if (study[stage.stage] == 1) {
                studies.push(study);
            } else {
                
            }
        }
        this.vpp.studies = studies;
    },

    parse_summary_results: function(data) {
        var xml = $(data);
        var docsums = xml.find('DocSum');
        var studies = [];
        
        for (let i = 0; i < docsums.length; i++) {
            var docsum_xml = $(docsums[i]);

            // get PMID
            var pmid = docsum_xml.find('Id')[0].textContent;

            // get title
            var title = docsum_xml.find('Item[Name="Title"]')[0].textContent;

            // get authors
            var authors = [];
            var authors_elems = docsum_xml.find('Item[Name="Author"]');
            for (let j = 0; j < authors_elems.length; j++) {
                var elem = authors_elems[j];
                authors.push(elem.textContent);
            }

            // get journal
            var journal = docsum_xml.find('Item[Name="FullJournalName"]')[0].textContent;

            // get date
            var date = docsum_xml.find('Item[Name="PubDate"]')[0].textContent;

            // update the record
            for (let j = 0; j < this.all_rs.length; j++) {
                if (pmid == this.all_rs[j].pmid) {
                    this.all_rs[j].title = title;
                    this.all_rs[j].date = date;
                    this.all_rs[j].journal = journal;
                    this.all_rs[j].authors = authors.join(', ');
                }
                
            }
        }
    }
}