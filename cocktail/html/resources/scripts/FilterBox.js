/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {

    jQuery(".FilterBox", root).each(function () {
        
        var filterBox = this;
        var filterList = jQuery(".filter_list", this).get(0);

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
            jQuery(".deleteButton", this)
                .attr("href", "javascript:")
                .click(function () {
                                        
                    // Shift the indices in filter fields
                    for (var i = filterEntry.index + 1; i < filterList.childNodes.length; i++) {
                        var sibling = filterList.childNodes[i];
                        sibling.index--;
                        jQuery("[name]", sibling).each(function () {
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

        jQuery(".new_filter_selector .selector_content a")
            .attr("href", "javascript:")
            .click(function () {
                cocktail.foldSelectors();
                filterBox.addUserFilter(this.filterId);
                return false;
            });
        
        // TODO: Client-side implementation for the 'delete filter' button
    });
});
