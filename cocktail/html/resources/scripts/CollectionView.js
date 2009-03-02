cocktail.init(function () {
            
    jQuery(".CollectionView").each(function () { 

        // Row activation
        if (this.activationControl) {
            var collectionView = this;
            jQuery(".collection_display", this).bind("activated", function () {
                jQuery(collectionView.activationControl, collectionView).click();
            });
        }

        // Selection controls
        var table = jQuery(".Table", this).get(0);

        if (table && this.hasResults) {
            
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
            jQuery(selectAllControl).click(function () { table.selectAll(); });
            selectionControls.appendChild(selectAllControl);

            // Clear selection
            var clearSelectionControl = document.createElement("a");
            clearSelectionControl.className = "clear_selection";
            clearSelectionControl.appendChild(document.createTextNode(
                cocktail.translate("cocktail.html.CollectionView clear selection")
            ));
            jQuery(clearSelectionControl).click(function () { table.clearSelection(); });
            selectionControls.appendChild(clearSelectionControl);
        }
    });
});
