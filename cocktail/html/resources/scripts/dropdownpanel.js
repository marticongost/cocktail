/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".DropdownPanel", function ($dropdown) {

    var $button = $dropdown.children(".button");

    this.getCollapsed = function () {
        return !$dropdown.hasClass("DropdownPanel-expanded");
    }

    this.setCollapsed = function (collapsed, focus /* = false */) {
        if (!collapsed) {
            jQuery(".DropdownPanel-expanded").each(function () {
                this.setCollapsed(true);
            });
        }
        $dropdown[collapsed ? "removeClass" : "addClass"]("DropdownPanel-expanded");
        if (focus) {
            if (collapsed) {
                $button.focus();
            }
            else {
                $dropdown.find(".panel :input:visible[tabindex!='-1'], .panel a:visible[tabindex!='-1']").first().focus();
            }
        }
        $dropdown.trigger(collapsed ? "collapsed" : "expanded");
        $dropdown.find(".exposable").trigger(collapsed ? "concealed" : "exposed");
    }

    this.toggleCollapsed = function (focus /* = false */) {
        this.setCollapsed(!this.getCollapsed(), focus);
    }

    $dropdown
        .click(function (e) { e.stopPropagation(); })
        .keydown(function (e) {
            if (e.keyCode == 27) {
                $dropdown.get(0).setCollapsed(true, true);
                return false;
            }
        });

    $button
        .click(function () { $dropdown.get(0).toggleCollapsed(true); })
        .keydown(function (e) {
            if (e.keyCode == 13) {
                $dropdown.get(0).toggleCollapsed(true);
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

