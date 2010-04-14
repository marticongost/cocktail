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
            var $selectable = jQuery(selectable);
            selectable.entrySelector = entrySelector;
            selectable._getEntries = function () { return $selectable.find(entrySelector); }
            selectable._selectionStart = null;
            selectable._selectionEnd = null;            
            selectable.selectionMode = selectionMode;
            
            // Create a dummy link element to fake focus for the element
            focusTarget = document.createElement('a');
            focusTarget.href = "javascript:;";
            focusTarget.className = "target_focus";
            $selectable.prepend(focusTarget);

            var suppressSelectionEvents = false;

            function batchSelection(func) {
                suppressSelectionEvents = true;
                try {
                    func.call(selectable);
                }
                catch (ex) {
                    throw ex;
                }
                finally {
                    suppressSelectionEvents = false;
                }
                $selectable.trigger("selectionChanged");
            }

            function handleFocus(updateSelection /* optional*/) {
                focusedSelectable = selectable;
                $selectable.addClass("focused");

                if (updateSelection !== false
                && !selectable._selectionStart
                && selectable._getEntries().length) {
                    selectable.setEntrySelected(selectable._getEntries()[0], true);
                }
            }

            function handleBlur() {
                focusedSelectable = null;
                $selectable.removeClass("focused");
            }
        
            jQuery(focusTarget)
                .focus(handleFocus)
                .blur(handleBlur);
            
            $selectable.find(entryCheckboxSelector)
                .focus(handleFocus)
                .blur(handleBlur);            

            // Double clicking selectable._getEntries() (change the selection and trigger an 'activated'
            // event on the table)

            selectable.dblClickEntryEvent = function (e) {
                selectable.clearSelection();                
                selectable.setEntrySelected(this, true);
                $selectable.trigger("activated");
            }

            selectable._getEntries().bind("dblclick", selectable.dblClickEntryEvent);
        
            selectable.getNextEntry = function (entry) {                
                var $entries = this._getEntries();
                var i = $entries.index(entry);                
                return (i == -1 || i == $entries.length) ? null : $entries[i + 1];
            }

            selectable.getPreviousEntry = function (entry) {
                var $entries = this._getEntries();
                var i = $entries.index(entry);
                return (i < 1) ? null : $entries[i - 1];
            }

            selectable.entryIsSelected = function (entry) {
                return jQuery(entry).hasClass("selected");
            }

            selectable.getSelection = function () {
                return selectable._getEntries().filter(":has(" + checkboxSelector + ":checked)");
            }

            selectable.setEntrySelected = function (entry, selected, scroll /* = false */) {
                
                jQuery(checkboxSelector, entry).get(0).checked = selected;

                if (selected) {
                    selectable._selectionStart = entry;
                    selectable._selectionEnd = entry;
                    jQuery(entry).addClass("selected");

                    if (scroll && entry.scrollIntoView) {
                        entry.scrollIntoView();
                    }
                }
                else {
                    jQuery(entry).removeClass("selected");
                }

                if (!suppressSelectionEvents) {
                    $selectable.trigger("selectionChanged");
                }
            }

            selectable.clearSelection = function () {
                batchSelection(function () {
                    selectable._getEntries().filter(".selected").each(function () {
                        selectable.setEntrySelected(this, false);
                    });
                });
            }

            selectable.selectAll = function () {
                batchSelection(function () {
                    selectable._getEntries().each(function () {
                        selectable.setEntrySelected(this, true);
                    });
                });
            }

            selectable.setRangeSelected = function (firstEntry, lastEntry, selected) {
                
                var entries = selectable._getEntries();
                var i = entries.index(firstEntry);
                var j = entries.index(lastEntry);
                
                var pos = Math.min(i, j);
                var end = Math.max(i, j);

                batchSelection(function () {
                    for (; pos <= end; pos++) {
                        this.setEntrySelected(entries[pos], selected);
                    }
                });

                selectable._selectionStart = firstEntry;
                selectable._selectionEnd = lastEntry;
            }

            selectable.clickEntryEvent = function (e) {

                var src = (e.target || e.srcElement);
                var srcTag = src.tagName.toLowerCase();
                var multipleSelection = (selectionMode == cocktail.MULTIPLE_SELECTION);

                handleFocus(false);

                if (srcTag != "a" && !jQuery(src).parents("a").length
                    && srcTag != "button" && !jQuery(src).parents("button").length
                    && srcTag != "textarea"
                    && (srcTag != "input" || jQuery(src).is(entryCheckboxSelector))
                ) {
                    // Range selection (shift + click)
                    if (multipleSelection && e.shiftKey) {
                        selectable.clearSelection();
                        selectable.setRangeSelected(selectable._selectionStart || selectable._getEntries()[0], this, true);
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

            selectable._getEntries()
                // Togle entry selection when clicking an entry
                .bind("click", selectable.clickEntryEvent)
                
                // Highlight selected entries
                .each(function () {
                    if (jQuery(checkboxSelector + ":checked", this).length) {
                        jQuery(this).addClass("selected");
                    }
                });
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
            jQuery(focusedSelectable).trigger("activated");
			return false;
        }
        // Home key
        else if (key == 36) {

            focusedSelectable.clearSelection();
            var firstEntry = focusedSelectable._getEntries()[0];

            if (multipleSelection && e.shiftKey) {
                focusedSelectable.setRangeSelected(
                    focusedSelectable._selectionStart,
                    firstEntry,
                    true);
            }
            else {
                focusedSelectable.setEntrySelected(firstEntry, true, true);
            }

            return false;
        }
        // End key
        else if (key == 35) {

            focusedSelectable.clearSelection();
            var lastEntry = focusedSelectable._getEntries()[focusedSelectable._getEntries().length - 1];

            if (multipleSelection && e.shiftKey) {
                focusedSelectable.setRangeSelected(focusedSelectable._selectionStart, lastEntry, true);
            }
            else {  
                focusedSelectable.setEntrySelected(lastEntry, true, true);
            }

            return false;
        }
        // Down key
        else if (key == 40) {
            
            var nextEntry = focusedSelectable._selectionEnd
                         && focusedSelectable.getNextEntry(focusedSelectable._selectionEnd);

            if (nextEntry) {
                focusedSelectable.clearSelection();
                            
                if (multipleSelection && e.shiftKey) {
                    focusedSelectable.setRangeSelected(
                        focusedSelectable._selectionStart, nextEntry, true);
                }
                else {
                    focusedSelectable.setEntrySelected(nextEntry, true, true);
                }
            }

            return false;
        }
        // Up key        
        else if (key == 38) {
               
            var previousEntry = focusedSelectable._selectionEnd
                             && focusedSelectable.getPreviousEntry(focusedSelectable._selectionEnd);

            if (previousEntry) {
                focusedSelectable.clearSelection();
            
                if (multipleSelection && e.shiftKey) {
                    focusedSelectable.setRangeSelected(
                        focusedSelectable._selectionStart, previousEntry, true);
                }
                else {
                    focusedSelectable.setEntrySelected(previousEntry, true, true);
                }
            }

            return false;
        }
    });
})();

cocktail.init(function (root) {
    jQuery(".selectable", root).each(function () {
        var params = this.selectableParams || {};
        params.element = this;
        cocktail.selectable(params);
    });
});

