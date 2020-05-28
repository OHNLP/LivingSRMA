var tb_studylist = {
    vpp: null,
    vpp_id: '#tb-studylist',
    data: {},
    width: 400,
    
    all_rs: [
        { pmid: '31079938', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 0, b7: 0, e1: 0, e2: 0, e3: 0, a1: 1, a2: 1, a3: 1, u1: 0, u2: 0, f1: 1, f2: 1 },
        { pmid: '30779531', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 1, e1: 0, e2: 0, e3: 0, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 1 },
        { pmid: '29562145', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 1, e1: 0, e2: 0, e3: 0, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 1 },
        { pmid: '28199818', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 1, e1: 0, e2: 0, e3: 0, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 1 },
        { pmid: '23964934', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 1, e1: 0, e2: 0, e3: 0, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 1 },
        { pmid: '24019545', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 1, e1: 0, e2: 0, e3: 0, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 1 },
        { pmid: '24206640', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 1, e1: 0, e2: 0, e3: 0, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 1 },
        { pmid: '27918762', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 0, e1: 0, e2: 0, e3: 1, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 0 },
        { pmid: '25952317', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 0, e1: 0, e2: 0, e3: 1, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 0 },
        { pmid: '30529901', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 0, e1: 0, e2: 0, e3: 1, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 0 },
        { pmid: '31427204', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 1, e1: 0, e2: 0, e3: 0, a1: 1, a2: 0, a3: 0, u1: 1, u2: 1, f1: 1, f2: 1 },
        // two abstract
        { pmid: 'NCT01481870', title: 'Comparison of Sequential Therapies With Sunitinib and Sorafenib in Advanced Renal Cell Carcinoma (CROSS-J-RCC)', date: 'December 2015', journal: 'ClinicalTrials.gov', authors: 'Yoshihiko TOMITA, Yamagata University', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 1, e1: 0, e2: 0, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 1 },
        { pmid: 'NCT01984242', title: 'A Study of Atezolizumab (an Engineered Anti-Programmed Death-Ligand 1 [PD-L1] Antibody) as Monotherapy or in Combination With Bevacizumab (Avastin®) Compared to Sunitinib (Sutent®) in Participants With Untreated Advanced Renal Cell Carcinoma (IMmotion150)', date: 'January 8, 2019', journal: 'ClinicalTrials.gov', authors: 'Hoffmann-La Roche', b1: 1, b2: 1, b3: 1, b4: 1, b5: 1, b6: 1, b7: 1, e1: 0, e2: 0, a1: 0, a2: 0, a3: 0, u1: 0, u2: 0, f1: 1, f2: 1 },

    ],
    
    load: function() {
        // load data of these pmids:
        var pmids = this.unpack(this.all_rs.slice(0, 11), 'pmid');
        this.get_summary_of_search_results(pmids, function(data) {
            tb_studylist.parse_summary_results(data);
            tb_studylist.init();
            tb_studylist.update_study_list({ 
                stage: 'f2', 
                number: 10, 
                text: 'Final number in quantitative synthesis (meta-analysis)' 
            });
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
        this.vpp.stage = stage;
        // filter the studies
        var studies = [];
        for (let i = 0; i < this.all_rs.length; i++) {
            const study = this.all_rs[i];
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
                const elem = authors_elems[j];
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