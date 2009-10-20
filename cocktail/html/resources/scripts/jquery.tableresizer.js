/**
 * jQuery TableResizer
 *
 * A lightweight plugin that creates resizable tables
 *
 **/

(function($) {

$.fn.tableresizer = function(options) 
{        
    $.fn.tableresizer.defaults = 
    {
        col_border : "2px solid #666",
        row_border : "2px solid #666",
        row_start  : "1"
    };
    
    // default options used on initialisation
    // and arguments used on later calls
    var opts = $.extend({}, $.fn.tableresizer.defaults, options);
    var args = arguments;
    
    /**
     * Make table columns resizable
     */  
    var resize_columns = function(root)
    {           
        var tbl = root.children("table");
        tbl.find("td").width(0);
        var tr  = tbl.find("tr:first");
        var header;
        var resize = false;
        
        /*
        if(tbl.get(0).total_width>tbl.get(0).min_width){
            root.width(tbl.get(0).total_width);
        }else{
            root.width(tbl.get(0).min_width);
        }
        */
        root.width(tbl.get(0).min_width);
        tbl.width(tbl.get(0).min_width)
        
        tr.children("th").css("border-right",opts.col_border);
        var left_pos = root.offset().left;
        
        saveCookiesWidth = function()
        {
			var colWidth = [];
			tr.children("th").each(function(index) {
				if(index > 0){
					var col_w = jQuery(this).width();
					colWidth.push(this.className + "=" + col_w);
				}
			});
			var expire = new Date();
			expire.setDate(expire.getDate() + 365); // year
			jQuery.cookie(tbl.get()[0].id + "-width", colWidth.join("+"), {
				expires: expire.toGMTString(),
				path:"/"
			});
        };
    
        endresize = function()
        {			
            if(resize == true && header != null)
            {
                document.onselectstart=new Function ("return true");
                resize = false;
                tbl.css("cursor","");
				saveCookiesWidth();
            }
        };
        
        tbl.mousemove(function(e)
        {
            var left = (e.clientX - left_pos);
    
            if(resize)
            {
                // when jquery includes dimensions into core, use that
                // to get implicit with instead of subtracting padding                
                var width = left - (header.offset().left - left_pos - jQuery(document).scrollLeft())
                    - parseInt(header.css("padding-left"))
                    - parseInt(header.css("padding-right"));                
    
                if(width > 1)
                {
                    var current_width = header.width();
                    // If expanding, resize container first, else resize
                    // column then container. otherwise the adjacent 
                    // cells resize
                    if(width > current_width)
                    {
                        var total = root.width() + ((width - header.width()));
                        root.width(total);
                        header.width(width);
                    }
                    else
                    {
                        header.width(width);
                        // check the header resize (might have
                        // a min width
                        if(header.width() == width)
                        {
                            var total = root.width() + ((width - current_width));
                            root.width(total);
                        }
                    }
                    newwidth = width;
                }
               
            }
            else
            {
                if(e.target.nodeName == "TH")
                {                
                    // nasty calculation to check the mouse is on / around
                    // the border to a header
                    var tgt = $(e.target);
                    var dosize = (left-(tgt.offset().left-left_pos-jQuery(document).scrollLeft()) 
                        > tgt.width() + 10);
                    $(this).css("cursor",dosize?"col-resize":"");
                }
            }                   
        });
        
        tbl.mouseup(function(e) 
        {
            endresize();
        });
                
        tbl.bind("mouseleave",function(e)
        {			
            endresize();
            return false; 
        });
        
        tr.mousedown(function(e) 
        {   
            if(e.target.nodeName == "TH" 
                && $(this).css("cursor") ==  "col-resize")
            {
                header = $(e.target);                
                resize = true;				
                // Stop ie selecting text
                document.onselectstart=new Function ("return false");
            }            
        });
        
        tr.bind('mouseleave',function(e)
        {
            if(!resize)
                tbl.css("cursor","");
        });
    };
    
    /**
     * Make table rows resizable
     */  
    var resize_rows = function(root)
    {        
        var tbl = root.find("table");
        var row,newheight;
        var rows = root.find(tbl.get(0).resizableRowsSelector || "tbody tr").children("td:visible");
        var resize = false;
        var top = root.offset().top;
		

        rows.css("border-bottom",opts.row_border);

		saveCookiesHeight = function()
        {
			var rowHeight = [];
			rows.each(function() {
				rowHeight.push(jQuery(this).parent("tr").attr("id") + "=" + jQuery(this).height());
			});
			var expire = new Date();
			expire.setDate(expire.getDate() + 365); // year
			jQuery.cookie(tbl.get()[0].id + "-height", rowHeight.join("+"), {
				expires: expire.toGMTString(),
				path:"/"
			});
        }

        rows.mousemove(function(e)
        {
            var x = (e.clientY - top) + document.documentElement.scrollTop;
    
            if(resize)
            {
                var height = x - (row.offset().top - top);                
                row.height(height);
                //newheight = height;
            }
    
            else
            {
                var cursor = (x - ($(this).offset().top - top) 
                    > $(this).height() + 10) ? "row-resize" : "";
                tbl.css("cursor",cursor);				
            }
        });         

        rows.mousedown(function(e) 
        {
            if(tbl.css("cursor") ==  "row-resize")
            {
                row = $(e.target);
                row.parent("tr").unbind("click");
                resize = true;                
                // Stop ie selecting text
                document.onselectstart=new Function ("return false");
            }
            return false;
        });

        tbl.click(function(e){            
            if(tbl.get(0).clickEntryEvent && e.target.nodeName == "TD"){
                $(e.target).parent("tr").bind("click", tbl.get(0).clickEntryEvent);
            }
        });

        tbl.mouseup(function(e) 
        {
            if(resize){
				document.onselectstart=new Function ("return true");				
				resize = false;
				tbl.css("cursor","");			
                row = null;
                saveCookiesHeight();
			}
        });
    };

	var parseCookie = function(data, table, direction) {
		if(direction == "width"){
			columns = data.split("+");
            var total = 0;
            document.getElementById(table).min_width = jQuery("#" + table).innerWidth();
			for (var i=0; i<columns.length; i++) {
				column_data = columns[i].split("=");
				jQuery("#" + table + " ." + column_data[0].replace(/ /, ".")).width(parseInt(column_data[1]));
                total += parseInt(column_data[1]);
			}
        document.getElementById(table).total_width = total;
		}else if(direction == "height"){
			rows = data.split("+");
			for (var i=0; i<rows.length; i++) {
				row_data = rows[i].split("=");
				jQuery("#" + table + " tr#" + row_data[0]).children("td:nth-child(" + opts.row_start + ")").height(parseInt(row_data[1]));
			}
		}
	};
    
    /**
     * Entry point
     */   
    return this.each(function(index) 
    {        		
		if (!this.persistencePrefix){ 
            this.id = 'table-' + (index + 1);
        }else{
            this.id = 'table-' + this.persistencePrefix.substr(this.persistencePrefix.lastIndexOf(".") + 1, this.persistencePrefix.length);			
        }
	    /*	
		if(jQuery.cookie(this.id + "-width")){
			parseCookie(jQuery.cookie(this.id + "-width"), this.id, "width");
		}
        */
		if(jQuery.cookie(this.id + "-height")){
			parseCookie(jQuery.cookie(this.id + "-height"), this.id, "height");
		}

    	var root = $(this).wrap("<div class='roottbl' />").parent();   
		//resize_columns(root);
        resize_rows(root);    
    });
};

})(jQuery);

cocktail.init(function (root) {
    var opts = {
        row_border:"1px solid #E1E1E1",
        col_border:"1px solid #E1E1E1",
        row_start: "2"
    }
    jQuery(".resizable", root).tableresizer(opts);          
});
