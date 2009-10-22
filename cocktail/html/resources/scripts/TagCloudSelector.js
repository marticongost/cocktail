/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {

    jQuery(".TagCloudSelector", root).each(function () {

        function update() {
            var $parent = jQuery(this.parentNode);
            if (this.checked) {
                $parent.addClass("selected");
            }
            else {
                $parent.removeClass("selected");
            }
        }

        jQuery(".entry input", this)
            .hide()
            .each(update)
            .change(update);
    });
});

