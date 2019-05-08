/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
-----------------------------------------------------------------------------*/

cocktail.bind(".FilterBox", function ($filterBox) {

    var filterList = jQuery(this).find(".filter_list").get(0);

    this.addUserFilter = function (filterId) {
        var index = filterList.childNodes.length;
        var $entry = jQuery(cocktail.instantiate(
            "cocktail.html.FilterBox-entry-" + filterId,
            {index: index},
            function () {
                this.style.display = "none";
                this.index = index;
                filterList.appendChild(this);
            }
        ));
        initFilterEntry.call($entry[0]);
        $entry.show("normal");
        return $entry;
    }

    var filterSuffixExpr = /\d+$/;

    function initFilterEntry() {
        var filterEntry = this;
        jQuery(this).find(".delete_filter_button")
            .attr("href", "javascript:")
            .click(function () {

                // Shift the indices in filter fields
                for (var i = filterEntry.index + 1; i < filterList.childNodes.length; i++) {
                    var sibling = filterList.childNodes[i];
                    sibling.index--;
                    jQuery(sibling).find("[name]").each(function () {
                        this.name = this.name.replace(filterSuffixExpr, i - 1);
                    });
                }

                filterList.removeChild(filterEntry);
                return false;
            });
    }

    for (var i = 0; i < filterList.childNodes.length; i++) {
        var filterEntry = filterList.childNodes[i];
        filterEntry.index = i;
        initFilterEntry.call(filterEntry);
    }

    var $newFilterSelector = $filterBox.find(".new_filter_selector");
    var $panel = $newFilterSelector.find(".panel");

    $panel.find("a")
        .attr("href", "javascript:")
        .click(function (e) {
            cocktail.foldSelectors();
            var $entry = $filterBox.get(0).addUserFilter(this.filterId);
            e.preventDefault();
            $newFilterSelector[0].setCollapsed(true);
            $entry.find(":input:visible").first().focus();
            $entry.find(".value_field :input:visible").first().focus();
        });

    var $searchBox = jQuery("<input type='search'>")
        .addClass("search_box")
        .prependTo($panel);

    cocktail.searchable($panel, {
        entriesSelector: "a",
        highlighted: true
    });

    // TODO: Client-side implementation for the 'delete filter' button
});
