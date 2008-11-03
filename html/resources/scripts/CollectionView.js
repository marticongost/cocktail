cocktail.translate("CollectionView selection");
cocktail.translate("CollectionView all");
cocktail.translate("CollectionView none");


jQuery(function () {
    
    var checkboxes = jQuery(".Table .selection input");
    var lastSelected;
    
    jQuery(document).keydown(function (e) {                                        
           
        if(!lastSelected){
            lastSelected = checkboxes[0];    
        }
        
        var key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;            
        var selindex = checkboxes.index(lastSelected);
        
		switch(key) {    		   
			case 38: 			  
			  if(selindex > 0){		  
			    if ( !e.shiftKey ) removeSelection();
			    lastSelected = checkboxes[selindex-1];
			    lastSelected.checked = true;
                highlightSelection.call(checkboxes[selindex-1]);			      
			  };
			  break;
			case 40: 
			  if(checkboxes.length > selindex+1) {
			    if ( !e.shiftKey ) removeSelection();
			    lastSelected = checkboxes[selindex+1];
			    lastSelected.checked = true;
                highlightSelection.call(checkboxes[selindex+1]);
			  }
			  break;			     
		}
    });
      
    function highlightSelection() {
        var row = jQuery(this).parents("tr");

        if (this.checked) {
            row.addClass("selected");
        }
        else {
            row.removeClass("selected");
        }
    }

    // Hide checkboxes, but keep them around for form submission purposes
    jQuery(".Table .selection")
        .css({width: 0})
        .find("input").css({position: "absolute", left: "-1000px"});
    
    checkboxes
        .each(highlightSelection)
        .change(highlightSelection);
        
    function removeSelection() {
        jQuery(".Table .selection input:checked")
                        .each(function () {                        
                            this.checked = !this.checked;
                            highlightSelection.call(this);                    
        });    
    }
    
    function selectAll() {
        checkboxes.each( function () {
            this.checked = true;
            highlightSelection.call(this);
        });    
    }

    jQuery(".Table tbody tr")
        
        // Togle row selection when clicking a row
        .click(function (e) {
            
            var src = e.target || e.srcElement;
            var srcTag = src.tagName.toLowerCase();            

            if (srcTag != "label" && srcTag != "input" && srcTag != "button" && srcTag != "textarea") {
                
                if ( e.shiftKey ) {                    	                   
                    var selIndex = checkboxes.index(jQuery(this).find(".selection input").get(0));
                    var lastIndex = checkboxes.index(lastSelected);
                    /*
                     * if you find the "select/unselect" behavior unseemly,
                     * remove this assignment and replace 'checkValue'
                     * with 'true' below.
                     */
                    var checkValue = lastSelected.checked;
                    if ( selIndex == lastIndex ) {
                        return true;
                    }
        
                    var end = Math.max(selIndex,lastIndex);
                    var start = Math.min(selIndex,lastIndex);

                    for(i=start;i<=end;i++) {
                        checkboxes[i].checked = checkValue;
                        highlightSelection.call(checkboxes[i]);
                    }
                   
                }else{
                    
                    if ( !e.ctrlKey ) removeSelection();

                                  
                    lastSelected = jQuery(this).find(".selection input").get(0);
                    lastSelected.checked = !lastSelected.checked;                               
                    
                    highlightSelection.call(lastSelected);
                 
                }
            }                          
                        
        })

        .dblclick(function () {
        
            jQuery(".Table .selection input").each(function () {
                this.checked = false;
                highlightSelection.call(this);
            });

            if (jQuery(this).is(".Table tbody tr")) {
                var row = this;
            }
            else {
                var row = jQuery(this).parents(".Table tbody tr");
            }

            jQuery(row).find(".selection input").each(function () {
                this.checked = true;
                highlightSelection.call(this);
            });
            
            jQuery(".toolbar_button[value=edit]").click();
        });
        
        
        var texts = [
                {
                    text: cocktail.translate("CollectionView selection"),
                    cls: ''
                },
                {
                    text: cocktail.translate("CollectionView all"),
                    cls: 'row_selector_all'
                },
                {
                    text: cocktail.translate("CollectionView none"),
                    cls: 'row_selector_none'
                }
        ];
        
        
        var div = document.createElement('div');
        div.className = 'row_selector';
        
        for(i=0;i<texts.length;i++){            
            var span = document.createElement('span');
            
            if(texts[i].cls!=""){                 
                var link = document.createElement('a');
                link.className = texts[i].cls;
                link.appendChild(document.createTextNode(texts[i].text));
                span.appendChild(link);
            }else{
                span.appendChild(document.createTextNode(texts[i].text));
            }
            div.appendChild(span);
        }
        
        jQuery(".toolbar").after(div);
                        
        
        jQuery(".row_selector_all").click( function () {
            selectAll();
        });
        
        jQuery(".row_selector_none").click( function () {
            removeSelection();
        });
        
        
    function disableTextSelection () {
        
        var selector = jQuery(".Table");
        
        if (jQuery.browser.mozilla) {
            return selector.each(function() {
                jQuery(this).css({
                    'MozUserSelect' : 'none'
                });
            });
        } else if (jQuery.browser.msie) {
            return selector.each(function() {
                jQuery(this).bind('selectstart.disableTextSelect', function() {
                    return false;
                });
            });
        } else {
             return selector.each(function() {
                jQuery(this).bind('mousedown.disableTextSelect', function() {
                    return false;
                });
            });
        }
    } 
    
    disableTextSelection(); 
    
    /*
    function enableTextSelection () {
        
        var selector = jQuery(".Table");
        if (jQuery.browser.mozilla) {
            return selector.each(function() {
                jQuery(this).css({
                        'MozUserSelect' : ''
                });
            });
            
        } else if (jQuery.browser.msie) {
            return selector.each(function() {
                return this.each(function() {
                    jQuery(this).unbind('selectstart.disableTextSelect');
                });
            });
        } else {
             return selector.each(function() {
                return this.each(function() {
                    jQuery(this).unbind('mousedown.disableTextSelect');
                });
            });
        }
    }

    */
        
  
});