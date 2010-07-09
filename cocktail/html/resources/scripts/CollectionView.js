cocktail.bind(".CollectionView", function ($view) { 

    // Row activation
    if (this.activationControl) {
        $view.find(".collection_display").bind("activated", function () {
            $view.find($view.get(0).activationControl).click();
        });
    }

    // Selection controls
    var display = $view.find(".collection_display").get(0);

    if (display
        && this.hasResults
        && display.selectableParams
        && display.selectableParams.mode != cocktail.NO_SELECTION) {
        
        var selectionControls = document.createElement("div");
        selectionControls.className = "selection_controls";
        $view.find(".data_controls").prepend(selectionControls);
        
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

