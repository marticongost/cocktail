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
        var entry = cocktail.instantiate(
            "cocktail.html.FilterBox-entry-" + filterId,
            {index: index},
            function () {
                this.style.display = "none";
                this.index = index;
                filterList.appendChild(this);
            }
        );
        initFilterEntry.call(entry);
        jQuery(entry).show("normal");
    }

    var filterSuffixExpr = /\d+$/;

    function initFilterEntry() {
        var filterEntry = this;
        jQuery(this).find(".deleteButton")
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

    $filterBox.find(".new_filter_selector .selector_content a")
        .attr("href", "javascript:")
        .click(function () {
            cocktail.foldSelectors();
            $filterBox.get(0).addUserFilter(this.filterId);
            return false;
        });
    
    // TODO: Client-side implementation for the 'delete filter' button
});
