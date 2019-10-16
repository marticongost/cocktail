cocktail.bind(".CollectionView", function ($view) {

    // Row activation
    if (this.activationControl) {
        $view.find(".collection_display").bind("activated", function () {
            $view.find($view.get(0).activationControl).first().click();
        });
    }
});

