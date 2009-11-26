/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {

    jQuery(".selector", root)
        .addClass("scripted")
        .click(function (e) {
            var element = e.target || e.srcElement;
            if(element.tagName != "BUTTON") e.stopPropagation();
        })
        .children(".label")
            .each(function () {
                jQuery(this).replaceWith(
                    '<a href="javascript:;"'
                    + ' id="' + jQuery(this).attr('id') + '"'
                    + ' class="' + jQuery(this).attr('class') + '"'
                    + '>'
                    + jQuery(this).html()
                    + '</a>'
                );
            })
            .end()
        .children(".label").
            click(function (e) {
                var content_selector = jQuery(this).next(".selector_content");
                var selector = jQuery(this).parent(".selector");
                jQuery(".selector").not(selector).removeClass("unfolded");
                selector.toggleClass("unfolded");
                content_selector.find("input:first").focus();
                e.stopPropagation();
            });

    if (!cocktail.__Selector_clickEvent) {
        cocktail.__Selector_clickEvent = true;        
        jQuery(document).click(cocktail.foldSelectors);
    }
});

cocktail.foldSelectors = function () {
    jQuery(".selector").removeClass("unfolded");
}

