/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".DropdownPanel", function ($dropdown) {

    this.getCollapsed = function () {
        return !$dropdown.hasClass("DropdownPanel-expanded");
    }

    this.setCollapsed = function (collapsed) {
        $dropdown[collapsed ? "removeClass" : "addClass"]("DropdownPanel-expanded");
        if (!collapsed) {
            $dropdown.find(".panel *").first(function () { return this.focus; }).focus();
        }
    }

    this.toggleCollapsed = function () {
        this.setCollapsed(!this.getCollapsed());
    }

    $dropdown
        .click(function (e) { e.stopPropagation(); })
        .find(".button")
            .attr("tabindex", "0")
            .click(function () { $dropdown.get(0).toggleCollapsed(); })
            .keydown(function (e) {
                if (e.keyCode == 13) {
                    $dropdown.get(0).toggleCollapsed();
                    return false;
                }
                else if (e.keyCode == 27) {
                    $dropdown.get(0).setCollapsed(true);
                    return false;
                }
            });
});

jQuery(function () {
    jQuery(document).click(function () {
        jQuery(".DropdownPanel-expanded").each(function () {
            this.setCollapsed(true);
        });
    });
});

