/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".TextSizeBar", function ($textSizeBar) {
 
    var $target = jQuery("#" + this.textSizeTarget);

    this.setTextSize = function (newSize) {
        newSize = Math.max(-9, newSize);
        $target.removeClass("text_size-" + this.textSize);
        this.textSize = newSize;
        jQuery.cookie(this.textSizeCookie, newSize);
        $target
            .css("font-size", (100 + newSize * 10) + "%")
            .addClass("text_size-" + newSize);
    }

    this.changeTextSize = function (change) {
        this.setTextSize(this.textSize + change);
    }

    $textSizeBar.find(".decrease_size_button").click(function (e) {
        $textSizeBar.get(0).changeTextSize(-1);
        e.preventDefault();
    });

    $textSizeBar.find(".increase_size_button").click(function (e) {
        $textSizeBar.get(0).changeTextSize(1);
        e.preventDefault();
    });
});

