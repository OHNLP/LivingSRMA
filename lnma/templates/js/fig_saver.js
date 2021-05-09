var fig_saver = {
    date_format: d3.timeFormat('%Y_%m_%d_%H%M%S'),

    save: function(svg_id, fn) {
        var svg = d3.select(svg_id);
        this.save_png(svg, fn);
    },

    save_csv: function(data, filename) {
        /* data should contain:
        {
            header: [],
            tabledata: [{
                treat: 
                value:
                value_rank:
            }]
        }
        */
        var csv = '';
        csv += data.header.join(',') + '\n';
        for (let i = 0; i < data.tabledata.length; i++) {
            const r = data.tabledata[i];
            csv += r['treat'] + ',' + r['value'] + ',' + r['value_rank'] + '\n';
        }
        var blob = new Blob([csv], {type: 'text/csv;charset=utf-8'});
        
        var fn = filename + '_' + this.date_format(new Date()) + '.csv';
        saveAs(blob, fn);
    },

    save_png: function(d3svg, filename, scale_ratio) {
        function save( dataBlob, filesize ){
            var fn = filename + '_' + fig_saver.date_format(new Date()) + '.png';
            saveAs( dataBlob, fn);
        }
        var svgString = this.getSVGString(d3svg.node());
        var width = d3svg.attr('width') * 1;
        var height = d3svg.attr('height') * 1;
        // scale use to be 3.5
        if (typeof(scale_ratio) == 'undefined') {
            scale_ratio = 3.5;
        }
        this.svgString2Image( svgString, scale_ratio*width, scale_ratio*height, 'png', save );
    },

    getSVGString: function(svgNode) {
        svgNode.setAttribute('xlink', 'http://www.w3.org/1999/xlink');
        var cssStyleText = getCSSStyles( svgNode );
        appendCSS( cssStyleText, svgNode );

        var serializer = new XMLSerializer();
        var svgString = serializer.serializeToString(svgNode);
        svgString = svgString.replace(/(\w+)?:?xlink=/g, 'xmlns:xlink='); // Fix root xlink without namespace
        svgString = svgString.replace(/NS\d+:href/g, 'xlink:href'); // Safari NS namespace fix

        return svgString;

        function getCSSStyles( parentElement ) {
            var selectorTextArr = [];

            // Add Parent element Id and Classes to the list
            selectorTextArr.push( '#'+parentElement.id );
            for (var c = 0; c < parentElement.classList.length; c++)
                    if ( !contains('.'+parentElement.classList[c], selectorTextArr) )
                        selectorTextArr.push( '.'+parentElement.classList[c] );

            // Add Children element Ids and Classes to the list
            var nodes = parentElement.getElementsByTagName("*");
            for (var i = 0; i < nodes.length; i++) {
                var id = nodes[i].id;
                if ( !contains('#'+id, selectorTextArr) )
                    selectorTextArr.push( '#'+id );

                var classes = nodes[i].classList;
                for (var c = 0; c < classes.length; c++)
                    if ( !contains('.'+classes[c], selectorTextArr) )
                        selectorTextArr.push( '.'+classes[c] );
            }

            // Extract CSS Rules
            var extractedCSSText = "";
            for (var i = 0; i < document.styleSheets.length; i++) {
                var s = document.styleSheets[i];
                
                try {
                    if(!s.cssRules) continue;
                } catch( e ) {
                        if(e.name !== 'SecurityError') throw e; // for Firefox
                        continue;
                    }

                var cssRules = s.cssRules;
                for (var r = 0; r < cssRules.length; r++) {
                    if ( contains( cssRules[r].selectorText, selectorTextArr ) )
                        extractedCSSText += cssRules[r].cssText;
                }
            }
            

            return extractedCSSText;

            function contains(str,arr) {
                return arr.indexOf( str ) === -1 ? false : true;
            }

        }

        function appendCSS( cssText, element ) {
            var styleElement = document.createElement("style");
            styleElement.setAttribute("type","text/css"); 
            styleElement.innerHTML = cssText;
            var refNode = element.hasChildNodes() ? element.children[0] : null;
            element.insertBefore( styleElement, refNode );
        }
    },

    svgString2Image: function( svgString, width, height, format, callback ) {
        var format = format ? format : 'png';

        var imgsrc = 'data:image/svg+xml;base64,'+ btoa( unescape( encodeURIComponent( svgString ) ) ); // Convert SVG string to data URL

        var canvas = document.createElement("canvas");
        var context = canvas.getContext("2d");

        canvas.width = width;
        canvas.height = height;

        var image = new Image();
        image.onload = function() {
            context.clearRect ( 0, 0, width, height );
            context.drawImage(image, 0, 0, width, height);

            canvas.toBlob( function(blob) {
                var filesize = Math.round( blob.length/1024 ) + ' KB';
                if ( callback ) callback( blob, filesize );
            });
        };

        image.src = imgsrc;
    }

}
