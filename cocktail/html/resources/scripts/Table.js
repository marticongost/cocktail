/*-----------------------------------------------------------------------------


@author:		Martí Congost
@author:		Cèsar Ebrat
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
-----------------------------------------------------------------------------*/

cocktail.init(function () {

    var focusedTable = null;

    jQuery(".Table").each(function () {
        
        jQuery(this).addClass("resizable");

        if (this.selectionMode == cocktail.NO_SELECTION) {
            return;
        }

        // Create a dummy link element to fake focus for the table
        focusTarget = document.createElement('a');
        focusTarget.href = "javascript:;";
        focusTarget.className = "target_focus";
        jQuery(this).prepend(focusTarget);

        function handleFocus() {
            var table = jQuery(this).parents(".Table").get(0);
            focusedTable = table;
            jQuery(table).addClass("focused");

            if (!table._selectionStart && table._rows.length) {
                table.setRowSelected(table._rows[0], true);
            }
        }

        function handleBlur() {
            var table = jQuery(this).parents(".Table").get(0);
            focusedTable = null;
            jQuery(table).removeClass("focused");
        }

        jQuery(focusTarget)
            .focus(handleFocus)
            .blur(handleBlur);
            
        jQuery("td.selection input", this)
            .focus(handleFocus)
            .blur(handleBlur);
            
        this._rows = jQuery("tbody tr", this);

        // Double clicking rows (change the selection and trigger an 'activated'
        // event on the table)
        this._rows.dblclick(function () {
            var table = jQuery(this).parents(".Table").get(0);
            table.clearSelection();
            table.setRowSelected(this, true);
            jQuery(table).trigger("activated");
        });

        // Row selection
        this._selectionStart = null;

        this.rowIsSelected = function (row) {
            return jQuery(row).hasClass("selected");
        }

        this.setRowSelected = function (row, selected) {
            
            jQuery("td.selection input", row).get(0).checked = selected;

            if (selected) {
                this._selectionStart = row;
                this._selectionEnd = row;
                jQuery(row).addClass("selected");
            }
            else {
                jQuery(row).removeClass("selected");
            }

            jQuery(jQuery(row).parents(".Table").get(0)).trigger("selectionChanged");
        }

        this.clearSelection = function () {
            this._rows.filter(".selected").each(function () {
                var table = jQuery(this).parents(".Table").get(0);
                table.setRowSelected(this, false);
            });
        }

        this.selectAll = function () {
            this._rows.each(function () {
                var table = jQuery(this).parents(".Table").get(0);
                table.setRowSelected(this, true);
            });
        }

        this.setRangeSelected = function (firstRow, lastRow, selected) {
            
            var i = this._rows.index(firstRow);
            var j = this._rows.index(lastRow);
            
            var pos = Math.min(i, j);
            var end = Math.max(i, j);

            for (; pos <= end; pos++) {
                this.setRowSelected(this._rows[pos], selected);
            }

            this._selectionStart = firstRow;
            this._selectionEnd = lastRow;
        }

        // Togle row selection when clicking a row
        this._rows.click(function (e) {

            var src = (e.target || e.srcElement);
            var srcTag = src.tagName.toLowerCase();
            var table = jQuery(this).parents(".Table").get(0);
            var multipleSelection = (table.selectionMode == cocktail.MULTIPLE_SELECTION);

            jQuery(table).find(".target_focus").focus();

            if (srcTag != "a" && srcTag != "button" && srcTag != "textarea"
                && (srcTag != "input" || jQuery(src).parents("td.selection").length)) {
                
                // Range selection (shift + click)
                if (multipleSelection && e.shiftKey) {
                    table.clearSelection();
                    table.setRangeSelected(table._selectionStart || table._rows[0], this, true);
                }
                // Cumulative selection (control + click)
                else if (multipleSelection && e.ctrlKey) {
                    table.setRowSelected(this, !table.rowIsSelected(this));
                }
                // Replacing selection (regular click)
                else {
                    table.clearSelection();
                    table.setRowSelected(this, true);
                }

                if (srcTag == "label") {
                    e.preventDefault();
                }
            }
        });
    });

    jQuery(document).keydown(function (e) {
        
        if (!focusedTable) {
            jQuery("body").enableTextSelect();    
            return true;
        }
        
        jQuery("body").disableTextSelect();

        var key = e.charCode || e.keyCode;
        var multipleSelection = (focusedTable.selectionMode == cocktail.MULTIPLE_SELECTION);

        // Enter key; trigger the 'activated' event
        if (key == 13) {
            focusedTable.trigger("activated");
        }
        // Home key
        else if (key == 36) {

            focusedTable.clearSelection();
            var firstRow = focusedTable._rows[0];

            if (multipleSelection && e.shiftKey) {
                focusedTable.setRangeSelected(focusedTable._selectionStart, firstRow, true);
            }
            else {  
                focusedTable.setRowSelected(firstRow, true);
            }
        }
        // End key
        else if (key == 35) {

            focusedTable.clearSelection();
            var lastRow = focusedTable._rows[focusedTable._rows.length - 1];

            if (multipleSelection && e.shiftKey) {
                focusedTable.setRangeSelected(focusedTable._selectionStart, lastRow, true);
            }
            else {  
                focusedTable.setRowSelected(lastRow, true);
            }
        }
        // Down key
        else if (key == 40) {
            
            var nextRow = focusedTable._selectionEnd
                       && focusedTable._selectionEnd.nextSibling;

            if (nextRow) {
                focusedTable.clearSelection();
                            
                if (multipleSelection && e.shiftKey) {
                    focusedTable.setRangeSelected(
                        focusedTable._selectionStart, nextRow, true);
                }
                else {
                    focusedTable.setRowSelected(nextRow, true);
                }
            }
        }
        // Up key        
        else if (key == 38) {
               
            var previousRow = focusedTable._selectionEnd
                       && focusedTable._selectionEnd.previousSibling;

            if (previousRow) {
                focusedTable.clearSelection();
            
                if (multipleSelection && e.shiftKey) {
                    focusedTable.setRangeSelected(
                        focusedTable._selectionStart, previousRow, true);
                }
                else {
                    focusedTable.setRowSelected(previousRow, true);
                }
            }
        }
    });

    ResizableColumns();    

});
