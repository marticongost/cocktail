/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".CollectionEditor", function ($collectionEditor) {

    $collectionEditor.children(".add_button").click(function () {
        $collectionEditor.get(0).appendEntry();
    });

    this.appendEntry = function (focus /* optional */) {
        var $entry = jQuery(cocktail.instantiate("cocktail.html.CollectionEditor.new_entry-" + this.id));
        $collectionEditor.children(".entries").append($entry);
        $entry.children(".remove_button").click(removeEntry);
        cocktail.init();
        if (focus || focus === undefined) {
            $entry.find(":input").first().focus();
        }
    }

    this.getNumberOfEntries = function () {
        return $collectionEditor.children(".entries").children().length;
    }

    this.setNumberOfEntries = function (requestedNumber, focus /* optional */) {
        var $entries = $collectionEditor.children(".entries").children();
        var diff = requestedNumber - $entries.length;
        if (diff > 0) {
            do {
                this.appendEntry(focus);
            }
            while (--diff);
        }
        else if (diff < 0) {
            $entries.slice(diff).remove();
        }
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

