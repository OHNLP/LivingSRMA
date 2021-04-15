var srv_pubmed = {
    ret: null,
    paper_dict: null,
    url: {
        esearch: 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed',
        esummary: 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed',
        efetch: "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed",
        view_pmid: 'https://www.ncbi.nlm.nih.gov/pubmed/?term='
    },
    
    efetch: function(ids, callback) {
        $.get(
            this.url.efetch,
            {id: ids.join(','), retmode:'xml'},
            callback, 'xml'
        );
    },

    parse_efetch_data: function(data) {
        var xml = $(data);
        var docs = xml.find('PubmedArticle');
        
        var paper_dict = {};
        for (var i = 0; i < docs.length; i++) {
            var doc = $(docs[i]);

            // get PMID
            var pmid = doc.find('PMID')[0].textContent;

            // get title
            var title = doc.find('ArticleTitle')[0].textContent;
            title = title.trim();

            // get title
            var abstract = doc.find('Abstract')[0].textContent;
            abstract = abstract.trim();

            // get authors
            var authors = [];
            var authors_elems = doc.find('Author');
            for (var j = 0; j < authors_elems.length; j++) {
                var elem = $(authors_elems[j]);
                var last_name = elem.find('LastName')[0].textContent;
                var fore_name = elem.find('ForeName')[0].textContent;
                var initials = elem.find('Initials')[0].textContent;
                var name = fore_name + ' ' + last_name;
                authors.push(name);
            }

            // get journal
            // var journal = doc.find('Journal Title')[0].textContent;
            var journal = doc.find('ISOAbbreviation')[0].textContent;

            // get date
            var pub_date = '';
            try {
                const y = doc.find('ArticleDate Year')[0].textContent;
                const m = doc.find('ArticleDate Month')[0].textContent;
                const d = doc.find('ArticleDate Day')[0].textContent;
                pub_date = y + '-' + m + '-' + d;
            } catch {
                try {
                    const y = doc.find('DateCompleted Year')[0].textContent;
                    const m = doc.find('DateCompleted Month')[0].textContent;
                    const d = doc.find('DateCompleted Day')[0].textContent;
                    pub_date = y + '-' + m + '-' + d;
                } catch {
                    try {
                        const y = doc.find('PubDate Year')[0].textContent;
                        const m = doc.find('PubDate Month')[0].textContent;
                        pub_date = y + '-' + m;
                    } catch {
                        pub_date = doc.find('Year')[0].textContent;
                    }
                }
            }
            pub_date = pub_date.trim();

            // update the record
            paper_dict[pmid] = {};
            paper_dict[pmid].pmid = pmid;
            paper_dict[pmid].title = title;
            paper_dict[pmid].abstract = abstract;
            paper_dict[pmid].authors = authors;
            paper_dict[pmid].journal = journal;
            paper_dict[pmid].pub_date = pub_date;

            // most important, bind this doc to paper
            paper_dict[pmid].xml = doc;
        }

        return paper_dict;
    },

    esummary: function(ids, callback) {
        $.get(
            this.url.esummary,
            {id: ids.join(',')},
            callback, 'xml'
        );
    },

    parse_esummary_data: function(data) {
        var xml = $(data);
        var docsums = xml.find('DocSum');
        
        var paper_dict = {};
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
            var pub_date = docsum_xml.find('Item[Name="PubDate"]')[0].textContent;

            // update the record
            paper_dict[pmid] = {};
            paper_dict[pmid].title = title;
            paper_dict[pmid].journal = journal;
            paper_dict[pmid].pub_date = pub_date;
            paper_dict[pmid].authors = authors;
        }
        return paper_dict;
    }
};