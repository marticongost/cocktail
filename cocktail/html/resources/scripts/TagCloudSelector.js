/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
-----------------------------------------------------------------------------*/

cocktail.bind(".TagCloudSelector", function ($selector) {

    function update() {
        var $parent = jQuery(this.parentNode);
        if (this.checked) {
            $parent.addClass("selected");
        }
        else {
            $parent.removeClass("selected");
        }
    }

    $selector.find(".entry input")
        .hide()
        .each(update)
        .change(update);
});

