/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
-----------------------------------------------------------------------------*/

(function () {
    
    var focusedSelectable = null;

    cocktail.selectable = function (params) {

        function getParam(key, defaultValue) {
            var value = params[key];
            return value !== undefined && value !== null ? value : defaultValue;
        }

        var selectionMode = getParam("mode", cocktail.SINGLE_SELECTION);

        if (selectionMode == cocktail.NO_SELECTION) {
            return;
        }

        var elementSelector = getParam("element");
        var entrySelector = getParam("entrySelector", ".entry");
        var checkboxSelector = getParam("checkboxSelector", "input[type=checkbox]");
        var entryCheckboxSelector = entrySelector + " " + checkboxSelector;

        jQuery(elementSelector).each(function () {

            var selectable = this;
            var selectableJQ = jQuery(selectable);
            selectable.entrySelector = entrySelector;
            selectable._entries = selectableJQ.find(entrySelector);
            selectable._selectionStart = null;
            selectable._selectionEnd = null;            
            selectable.selectionMode = selectionMode;
                        
            // Create a dummy link element to fake focus for the element
            focusTarget = document.createElement('a');
            focusTarget.href = "javascript:;";
            focusTarget.className = "target_focus";
            selectableJQ.prepend(focusTarget);

            function handleFocus(updateSelection /* optional*/) {
                focusedSelectable = selectable;
                selectableJQ.addClass("focused");

                if (updateSelection !== false
                && !selectable._selectionStart
                && selectable._entries.length) {
                    selectable.setEntrySelected(selectable._entries[0], true);
                }
            }

            function handleBlur() {
                focusedSelectable = null;
                selectableJQ.removeClass("focused");
            }
        
            jQuery(focusTarget)
                .focus(handleFocus)
                .blur(handleBlur);
            
            selectableJQ.find(entryCheckboxSelector)
                .focus(handleFocus)
                .blur(handleBlur);        

            // Double clicking selectable._entries (change the selection and trigger an 'activated'
            // event on the table)

            selectable.dblClickEntryEvent = function () {
                selectable.clearSelection();
                selectable.setEntrySelected(this, true);
                selectableJQ.trigger("activated");
            }

            selectable._entries.bind("dblclick", selectable.dblClickEntryEvent);
        
            selectable.entryIsSelected = function (entry) {
                return jQuery(entry).hasClass("selected");
            }

            selectable.getSelection = function () {
                return selectable._entries.filter(":has(" + checkboxSelector + ":checked)");
            }

            selectable.setEntrySelected = function (entry, selected) {
                
                jQuery(checkboxSelector, entry).get(0).checked = selected;

                if (selected) {
                    selectable._selectionStart = entry;
                    selectable._selectionEnd = entry;
                    jQuery(entry).addClass("selected");
                }
                else {
                    jQuery(entry).removeClass("selected");
                }

                selectableJQ.trigger("selectionChanged");
            }

            selectable.clearSelection = function () {
                selectable._entries.filter(".selected").each(function () {
                    selectable.setEntrySelected(this, false);
                });
            }

            selectable.selectAll = function () {
                selectable._entries.each(function () {                
                    selectable.setEntrySelected(this, true);
                });
            }

            selectable.setRangeSelected = function (firstEntry, lastEntry, selected) {
                
                var i = selectable._entries.index(firstEntry);
                var j = selectable._entries.index(lastEntry);
                
                var pos = Math.min(i, j);
                var end = Math.max(i, j);

                for (; pos <= end; pos++) {
                    this.setEntrySelected(selectable._entries[pos], selected);
                }

                selectable._selectionStart = firstEntry;
                selectable._selectionEnd = lastEntry;
            }

            selectable.clickEntryEvent = function (e) {

                var src = (e.target || e.srcElement);
                var srcTag = src.tagName.toLowerCase();
                var multipleSelection = (selectionMode == cocktail.MULTIPLE_SELECTION);

                handleFocus(false);

                if (srcTag != "a" && srcTag != "button" && srcTag != "textarea" && srcTag != "img" &&
                    (srcTag != "input" || jQuery(src).is(entryCheckboxSelector))) {
                    
                    // Range selection (shift + click)
                    if (multipleSelection && e.shiftKey) {
                        selectable.clearSelection();
                        selectable.setRangeSelected(selectable._selectionStart || selectable._entries[0], this, true);
                    }
                    // Cumulative selection (control + click)
                    else if (multipleSelection && e.ctrlKey) {
                        selectable.setEntrySelected(this, !selectable.entryIsSelected(this));
                    }
                    // Replacing selection (regular click)
                    else {
                        selectable.clearSelection();
                        selectable.setEntrySelected(this, true);
                    }

                    if (srcTag == "label") {
                        e.preventDefault();
                    }
                }
            }

            // Togle entry selection when clicking an entry
            selectable._entries.bind("click", selectable.clickEntryEvent);
        });
    }

    jQuery(document).keydown(function (e) {
        
        if (!focusedSelectable) {
            jQuery("body").enableTextSelect();
            return true;
        }
        
        jQuery("body").disableTextSelect();

        var key = e.charCode || e.keyCode;
        var multipleSelection = (focusedSelectable.selectionMode == cocktail.MULTIPLE_SELECTION);

        // Enter key; trigger the 'activated' event
        if (key == 13) {
            focusedSelectable.trigger("activated");
        }
        // Home key
        else if (key == 36) {

            focusedSelectable.clearSelection();
            var firstEntry = focusedSelectable._entries[0];

            if (multipleSelection && e.shiftKey) {
                focusedSelectable.setRangeSelected(
                    focusedSelectable._selectionStart,
                    firstEntry,
                    true);
            }
            else {  
                focusedSelectable.setEntrySelected(firstEntry, true);
            }
        }
        // End key
        else if (key == 35) {

            focusedSelectable.clearSelection();
            var lastEntry = focusedSelectable._entries[focusedSelectable._entries.length - 1];

            if (multipleSelection && e.shiftKey) {
                focusedSelectable.setRangeSelected(focusedSelectable._selectionStart, lastEntry, true);
            }
            else {  
                focusedSelectable.setEntrySelected(lastEntry, true);
            }
        }
        // Down key
        else if (key == 40) {
            
            var nextEntry = focusedSelectable._selectionEnd
                       && focusedSelectable._selectionEnd.nextSibling;

            if (nextEntry) {
                focusedSelectable.clearSelection();
                            
                if (multipleSelection && e.shiftKey) {
                    focusedSelectable.setRangeSelected(
                        focusedSelectable._selectionStart, nextEntry, true);
                }
                else {
                    focusedSelectable.setEntrySelected(nextEntry, true);
                }
            }
        }
        // Up key        
        else if (key == 38) {
               
            var previousEntry = focusedSelectable._selectionEnd
                       && focusedSelectable._selectionEnd.previousSibling;

            if (previousEntry) {
                focusedSelectable.clearSelection();
            
                if (multipleSelection && e.shiftKey) {
                    focusedSelectable.setRangeSelected(
                        focusedSelectable._selectionStart, previousEntry, true);
                }
                else {
                    focusedSelectable.setEntrySelected(previousEntry, true);
                }
            }
        }
    });
})();

cocktail.init(function () {
    jQuery(".selectable").each(function () {
        var params = this.selectableParams || {};
        params.element = this;
        cocktail.selectable(params);
    });
});

