jQuery(function () {

     var target = null;

     jQuery("*", document.body).each( function() {
         //Dbl click target selector
         if (this.dblclick_target) target = this.dblclick_target;
      });

    var target = target ? target : ".toolbar_button[value=edit]";

    //Switch selection type
    //TODO:

    var currentFocus = null;
    jQuery('input, textarea').focus( function() {
        currentFocus = this;
    }).blur( function() {
        currentFocus = null;
    });

    var checkboxes = jQuery(".Table .selection input");
    var lastSelected;

    jQuery(document).keydown(function (e) {

        if(!currentFocus){

            if(!lastSelected){
                lastSelected = checkboxes[0];
            }

            var key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
            var selindex = checkboxes.index(lastSelected);

    		switch(key) {
    		    case 13:
    		         if(jQuery(".Table .selection input:checked").length > 0) jQuery(target).click();
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
    			    setChecked(checkboxes[selindex-1], true);
    			  };
    			  break;
    			case 40:
    			  if(checkboxes.length > selindex+1) {
    			    if ( !e.shiftKey ) removeSelection();
    			    setChecked(checkboxes[selindex+1], true);                    
    			  }
    			  break;
    		}
    	}
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

    checkboxes
        .each(highlightSelection)
        .change(function () { setChecked(this, this.checked); });

    function removeSelection() {
        jQuery(".Table .selection input:checked").each(function () {
            setChecked(this, !this.checked);
        });
    }

    function selectAll() {
        checkboxes.each( function () {
            setChecked(this, true);
        });
    }

    jQuery(".Table tbody tr")

        // Togle row selection when clicking a row
        .click(function (e) {

            var src = e.target || e.srcElement;
            var srcTag = src.tagName.toLowerCase();

            if (srcTag != "a" && srcTag != "input" && srcTag != "button" && srcTag != "textarea") {

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

            jQuery(".Table .selection input").each(function () {
                setChecked(this, false);
            });

            if (jQuery(this).is(".Table tbody tr")) {
                var row = this;
            }
            else {
                var row = jQuery(this).parents(".Table tbody tr");
            }

            jQuery(row).find(".selection input").each(function () {
                setChecked(this, true);
            });

            jQuery(target).click();
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
});
