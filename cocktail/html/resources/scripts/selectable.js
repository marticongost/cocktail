/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
-----------------------------------------------------------------------------*/

(function () {
 
    var selectable = null;

    function disableTextSelection(element) {
        if (!element._hasTextSelectionDisabler) {
            element._hasTextSelectionDisabler = true;
            jQuery(element).bind('selectstart', function () {
                if (this.getAttribute("unselectable") == "on") {
                    return false;
                }
            });
        }
        jQuery(element)
            .attr('unselectable', 'on')
            .css('user-select', 'none');
    }

    function restoreTextSelection(element) {
        jQuery(element)
            .attr('unselectable', 'off')
            .css("user-select", "");
    }

    cocktail.selectable = function (params) {

        function getParam(key, defaultValue) {
            var value = params[key];
            return value !== undefined && value !== null ? value : defaultValue;
        }

        var selectionMode = getParam("mode", cocktail.SINGLE_SELECTION);
        var exclusiveSelection = getParam("exclusive", true);

        if (selectionMode == cocktail.NO_SELECTION) {
            return;
        }

        var multipleSelection = (selectionMode == cocktail.MULTIPLE_SELECTION);

        var elementSelector = getParam("element");
        var entrySelector = getParam("entrySelector", ".entry");
        var checkboxSelector = getParam("checkboxSelector", "input[type=checkbox]");
        var selectableEntryFilter = ":visible:has(" + checkboxSelector + ":enabled)";
        var entryCheckboxSelector = entrySelector + " " + checkboxSelector;

        jQuery(elementSelector).each(function () {

            var selectable = this;
            var $selectable = jQuery(selectable);
            selectable.entrySelector = entrySelector;

            selectable.getEntries = function (subset /* = null */) {
                var query = entrySelector;
                if (subset) {
                    query += normalizeEntrySelector(subset);
                }
                return $selectable.find(query);
            }

            selectable._selectionStart = null;
            selectable._selectionEnd = null;            
            selectable.selectionMode = selectionMode;
            
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

            function normalizeEntrySelector(selector) {
                return selector.replace(/:selectable-entry\b/g, selectableEntryFilter);
            }

            selectable.focusEntry = function (entry) {
                jQuery(entry).find(checkboxSelector).focus();
            }

            selectable.focusContent = function () {
                var entry = (this._selectionEnd || this._selectionStart);
                if (entry && jQuery(entry).is(selectableEntryFilter)) {
                    this.focusEntry(entry);
                }
                else {
                    var firstEntry = jQuery(this.getEntries(":selectable-entry"))[0];
                    if (exclusiveSelection) {
                        this.setEntrySelected(firstEntry, true, true);
                    }
                    else {
                        this.focusEntry(firstEntry);
                    }
                }
            }

            // Double clicking selectable.getEntries() (change the selection and trigger an 'activated'
            // event on the table)

            selectable.dblClickEntryEvent = function (e) {
                selectable.clearSelection();                
                selectable.setEntrySelected(this, true);
                $selectable.trigger("activated");
            }

            selectable.getEntries().bind("dblclick", selectable.dblClickEntryEvent);

            selectable.getNextEntry = function (entry, selector /* = null */) {

                var $entries = this.getEntries();
                
                var i = $entries.index(entry);
                if (i == -1) {
                    return null;
                }

                $entries = $entries.slice(i + 1);

                if (selector) {
                    $entries = $entries.filter(normalizeEntrySelector(selector));
                }

                return $entries.get(0);
            }

            selectable.getPreviousEntry = function (entry, selector /* = null */) {

                var $entries = this.getEntries();
                
                var i = $entries.index(entry);
                if (i == -1) {
                    return null;
                }

                $entries = $entries.slice(0, i);

                if (selector) {
                    $entries = $entries.filter(normalizeEntrySelector(selector));
                }

                return $entries.get(-1);
            }

            selectable.entryIsSelected = function (entry) {
                return jQuery(entry).hasClass("selected");
            }

            selectable.getSelection = function () {
                return selectable.getEntries().filter(":has(" + checkboxSelector + ":checked)");
            }

            selectable.setEntrySelected = function (entry, selected, focus /* = false */) {

                var checkBox = jQuery(checkboxSelector, entry).get(0);
                if (!checkBox) {
                    return;
                }
   
                checkBox.checked = selected;

                if (selected) {
                    selectable._selectionStart = entry;
                    selectable._selectionEnd = entry;
                    jQuery(entry).addClass("selected");

                    if (focus) {
                        selectable.focusEntry(entry);
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
                    selectable.getEntries().filter(".selected").each(function () {
                        selectable.setEntrySelected(this, false);
                    });
                });
            }

            selectable.selectAll = function () {
                batchSelection(function () {
                    selectable.getEntries().each(function () {
                        selectable.setEntrySelected(this, true);
                    });
                });
            }

            selectable.selectEntries = function (selector) {
                batchSelection(function () {
                    selectable.getEntries(selector).each(function () {
                        selectable.setEntrySelected(this, true);
                    });
                });
            }

            selectable.setRangeSelected = function (firstEntry, lastEntry, selected) {
                
                var entries = selectable.getEntries();
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

                if (srcTag != "a" && !jQuery(src).parents("a").length
                    && srcTag != "button" && !jQuery(src).parents("button").length
                    && srcTag != "textarea"
                    && (srcTag != "input" || jQuery(src).is(entryCheckboxSelector))
                ) {
                    // Range selection (shift + click)
                    if (multipleSelection && e.shiftKey) {
                        if (exclusiveSelection) {
                            selectable.clearSelection();
                        }
                        selectable.setRangeSelected(selectable._selectionStart || selectable.getEntries()[0], this, true);
                        selectable.focusEntry(this);
                    }
                    // Cumulative selection (control + click, or selector in non exclusive mode)
                    else if (multipleSelection && (e.ctrlKey || !exclusiveSelection)) {
                        selectable.setEntrySelected(this, !selectable.entryIsSelected(this), true);
                    }
                    // Select an element (regular click)
                    else {
                        selectable.clearSelection();
                        selectable.setEntrySelected(this, true, true);
                    }

                    if (srcTag == "label") {
                        e.preventDefault();
                    }
                }
            }

            selectable.getEntries()
                // Togle entry selection when clicking an entry
                .bind("click", selectable.clickEntryEvent)
                
                .mousedown(function () {
                    disableTextSelection(selectable);
                })

                .click(function() {
                    restoreTextSelection(selectable);
                })

                // Highlight selected entries
                .each(function () {
                    if (jQuery(checkboxSelector + ":checked", this).length) {
                        jQuery(this).addClass("selected");
                    }
                });

            var focusedCheckbox = null;

            $selectable.find(entrySelector + " " + checkboxSelector)
                .focus(function (e) {
                    focusedCheckbox = this;
                    var entry = jQuery(this).closest(entrySelector).get(0);
                    selectable._selectionEnd = entry;
                    $selectable.addClass("focused");
                })
                .blur(function (e) {
                    if (focusedCheckbox == this) {
                        focusedCheckbox = null;
                        $selectable.removeClass("focused");
                    }
                })
                .keydown(function (e) {

                    var key = e.charCode || e.keyCode;

                    // Enter key; trigger the 'activated' event
                    if (key == 13) {
                        $selectable.trigger("activated");
                        return false;
                    }

                    if (key == 65 && e.ctrlKey) {
                        // ctrl + shift + a: empty the selection
                        if (e.shiftKey) {
                            selectable.clearSelection();
                        }
                        // ctrl + a: select all visible entries
                        else {
                            selectable.selectEntries(":selectable-entry");
                        }
                        return false;
                    }

                    var entry = null;

                    // Home key
                    if (key == 36) {
                        entry = selectable.getEntries(":selectable-entry").get(0);
                    }
                    // End key
                    else if (key == 35) {
                        entry = selectable.getEntries(":selectable-entry").get(-1);
                    }
                    // Down key
                    else if (key == 40) {
                        entry = (
                            focusedCheckbox
                            && selectable.getNextEntry(
                                jQuery(focusedCheckbox).closest(entrySelector),
                                ":selectable-entry"
                            )
                        );
                    }
                    // Up key        
                    else if (key == 38) {
                        entry = (
                            focusedCheckbox
                            && selectable.getPreviousEntry(
                                jQuery(focusedCheckbox).closest(entrySelector),
                                ":selectable-entry"
                            )
                        );
                        if (!entry && selectable.topControl) {
                            selectable.topControl.focus();
                        }
                    }

                    if (entry) {

                        if (exclusiveSelection) {
                            selectable.clearSelection();
                        }

                        if (multipleSelection && e.shiftKey) {
                            selectable.setRangeSelected(selectable._selectionStart, entry, true);
                        }
                        else if (exclusiveSelection) {
                            selectable.setEntrySelected(entry, true);
                        }
                        else {
                            selectable._selectionStart = entry;
                            selectable._selectionEnd = entry;
                        }

                        selectable.focusEntry(entry);
                        return false;
                    }
                });
        });
    }
})();

cocktail.bind(".selectable", function () {
    var params = this.selectableParams || {};
    params.element = this;
    cocktail.selectable(params);
});

