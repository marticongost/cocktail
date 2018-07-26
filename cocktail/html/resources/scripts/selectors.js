/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
-----------------------------------------------------------------------------*/

cocktail.bind(".selector", function ($selector) {
    $selector.click(function (e) {
        var element = e.target || e.srcElement;
        if (element.tagName != "BUTTON") e.stopPropagation();
    });
    $selector.children(".label")
        .attr("tabindex", 0)
        .click(function (e) {
            jQuery(".selector").not($selector).removeClass("unfolded");
            $selector.toggleClass("unfolded");
            jQuery(this).next(".selector_content").find("input:first").focus();
            e.stopPropagation();
        });
});

jQuery(function () { jQuery(document).click(cocktail.foldSelectors); });

cocktail.foldSelectors = function () {
    jQuery(".selector").removeClass("unfolded");
}

