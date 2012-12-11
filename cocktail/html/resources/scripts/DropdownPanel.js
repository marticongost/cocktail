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
        if (collapsed) {
            disableTabIndex();
        }
        else {
            restoreTabIndex();
            $dropdown.find(".panel *").filter(function () {
                return this.focus && this.tabIndex >= 0;
            }).first().focus();
        }
    }

    this.toggleCollapsed = function () {
        this.setCollapsed(!this.getCollapsed());
    }

    function restoreTabIndex() {
        $dropdown.find(".panel *").each(function () {
            this.tabIndex = this.DropdownPanel_tabIndex;
        });
    }

    disableTabIndex();

    function disableTabIndex() {
        $dropdown.find(".panel *").each(function () {
            this.DropdownPanel_tabIndex = this.tabIndex;
            this.tabIndex = -1;
        });
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

