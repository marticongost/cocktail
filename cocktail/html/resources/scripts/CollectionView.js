cocktail.init(function (root) {
            
    jQuery(".CollectionView", root).each(function () { 

        // Row activation
        if (this.activationControl) {
            var collectionView = this;
            jQuery(".collection_display", this).bind("activated", function () {
                jQuery(collectionView.activationControl, collectionView).click();
            });
        }

        // Selection controls
        var display = jQuery(".collection_display", this).get(0);

        if (display
            && this.hasResults
            && display.selectableParams
            && display.selectableParams.mode != cocktail.NO_SELECTION) {
            
            var selectionControls = document.createElement("div");
            selectionControls.className = "selection_controls";
            jQuery(".data_controls", this).prepend(selectionControls);
            
            var label = document.createElement("span");
            label.appendChild(document.createTextNode(
                cocktail.translate("cocktail.html.CollectionView selection options")
            ));
            selectionControls.appendChild(label);

            // Select all
            var selectAllControl = document.createElement("a");
            selectAllControl.className = "select_all";
            selectAllControl.appendChild(document.createTextNode(
                cocktail.translate("cocktail.html.CollectionView select all")
            ));
            jQuery(selectAllControl).click(function () { display.selectAll(); });
            selectionControls.appendChild(selectAllControl);

            // Clear selection
            var clearSelectionControl = document.createElement("a");
            clearSelectionControl.className = "clear_selection";
            clearSelectionControl.appendChild(document.createTextNode(
                cocktail.translate("cocktail.html.CollectionView clear selection")
            ));
            jQuery(clearSelectionControl).click(function () { display.clearSelection(); });
            selectionControls.appendChild(clearSelectionControl);
        }
    });
});
