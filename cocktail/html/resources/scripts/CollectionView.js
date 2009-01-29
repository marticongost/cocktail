jQuery(function () {

     var target = null;

     jQuery("*", document.body).each( function() {
         //Dbl click target selector
         if (this.dblclick_target) target = this.dblclick_target;
      });

    var target = target ? target : ".toolbar_button[value=edit]";

    //Switch selection type
    
    jQuery(".Table").each(function () {
        
        focus_target = document.createElement('a');        
        jQuery(focus_target).attr({
            href: "javascript:;"
        }).addClass("target-focus");          
        jQuery(this).append(focus_target);  
        
        jQuery("tbody tr", this)

        // Togle row selection when clicking a row
        .click(function (e) {

            var src = e.target || e.srcElement;
            var srcTag = src.tagName.toLowerCase();

            if (srcTag != "a" && srcTag != "input" && srcTag != "button" && srcTag != "textarea") {
                
                focus_target.focus();
                
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
                        setChecked(checkboxes[i], checkValue);
                    }
                }
                else {
                    if ( !e.ctrlKey ) removeSelection();

                    lastSelected = jQuery(this).find(".selection input").get(0);
                    setChecked(lastSelected, !lastSelected.checked);
                }

                if(srcTag == "label") e.preventDefault();
            }
        })

        .dblclick(function () {

            jQuery(".selection input", this).each(function () {
                setChecked(this, false);
            });

            if (jQuery(this).is("tbody tr", this)) {
                var row = this;
            }
            else {
                var row = jQuery(this).parents("tbody tr", this);
            }

            jQuery(row).find(".selection input").each(function () {
                setChecked(this, true);
            });

            jQuery(target).click();
        });
        
        var currentFocus = false;
        jQuery('.target-focus', this).focus( function() {            
            currentFocus = true;
        }).blur( function() {
            currentFocus = false;
        });
        
        var checkboxes = jQuery(".selection input", this);
        var lastSelected;
        
        jQuery(document).keydown(function (e) {
                
                if(currentFocus){
                    
                    jQuery("body").disableTextSelect();
        
                    var key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
                    var selindex = checkboxes.index(lastSelected);
        
            		switch(key) {
            		    case 13:
            		         if(jQuery(".selection input:checked", this).length > 0) jQuery(target).click();
                          break;
            		    case 36:
            		        removeSelection();
                            if ( e.shiftKey ){
                                var lastIndex = checkboxes.index(checkboxes[0]);
                                var selIndex = checkboxes.index(lastSelected);
                                var end = Math.max(selIndex,lastIndex);
                                var start = Math.min(selIndex,lastIndex);
        
                                for(i=start;i<=end;i++) {
                                    setChecked(checkboxes[i], true);
                                }
                            }else{
                                lastSelected = checkboxes[0];
            			        setChecked(checkboxes[0], true);
                            }
                          break;
            		    case 35:
                            removeSelection();
                            if ( e.shiftKey ){
                                var lastIndex = checkboxes.index(checkboxes[checkboxes.length-1]);
                                var selIndex = checkboxes.index(lastSelected);
                                var end = Math.max(selIndex,lastIndex);
                                var start = Math.min(selIndex,lastIndex);
        
                                for(i=start;i<=end;i++) {
                                    setChecked(checkboxes[i], true);
                                }
                            }else{
                			    lastSelected = checkboxes[checkboxes.length-1];
                			    setChecked(lastSelected, true);
                            }
                          break;
            			case 38:
            			  if(selindex > 0){
            			    if ( !e.shiftKey ) removeSelection();
            			    lastSelected = checkboxes[selindex-1];
            			    setChecked(checkboxes[selindex-1], true);
            			  };
            			  break;
            			case 40:
            			  if(checkboxes.length > selindex+1) {
            			    if ( !e.shiftKey ) removeSelection();
            			    lastSelected = checkboxes[selindex+1];
            			    setChecked(checkboxes[selindex+1], true);                    
            			  }
            			  break;
            		}
            	}else{
            	    jQuery("body").enableTextSelect();    
            	}
        });
        
         checkboxes
        .each(highlightSelection)
        .change(function () { setChecked(this, this.checked); });
        
    });
    
    function setChecked(control, checked) {        
        control.checked = checked;
        highlightSelection.call(control);
        jQuery(control).trigger("selectionChanged");
    }

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
    jQuery(".Table .selection").css({display: "none"});

    function removeSelection() {
        jQuery(".Table .selection input:checked").each(function () {
            setChecked(this, !this.checked);
        });
    }

    function selectAll() {
        jQuery(".Table .selection input").each( function () {
            setChecked(this, true);
        });
    }

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

    if(jQuery(".no_results").length==0){

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

        var rowSelectorPrev = jQuery(".search_results_message");
        if (!rowSelectorPrev.length) {
            rowSelectorPrev = jQuery(".toolbar");
        }
        rowSelectorPrev.after(div);

        jQuery(".row_selector_all").click( function () {
            selectAll();
        });

        jQuery(".row_selector_none").click( function () {
            removeSelection();
        });
    }
    
});
