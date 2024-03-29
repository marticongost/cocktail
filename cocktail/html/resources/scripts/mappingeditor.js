/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".MappingEditor", function ($collectionEditor) {

    $collectionEditor.children(".add_button").click(function () {
        $collectionEditor.get(0).appendEntry();
    });

    this.appendEntry = function () {
        var entry = cocktail.instantiate("cocktail.html.MappingEditor.new_entry-" + this.id);
        $collectionEditor.children(".entries").append(entry);
        jQuery(entry).children(".remove_button").click(removeEntry);
        cocktail.init();
    }

    function removeEntry() {
        jQuery(this).closest(".entry").remove();
    }

    $collectionEditor
        .children(".entries")
        .children(".entry")
        .children(".remove_button")
            .click(removeEntry);
});

