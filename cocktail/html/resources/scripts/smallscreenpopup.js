/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         May 2016
-----------------------------------------------------------------------------*/

cocktail.bind(".SmallScreenPopUp", function ($popup) {

    this.togglePopUp = function () {
        this.setPopUpDisplayed(!this.getPopUpDisplayed());
    }

    this.getPopUpDisplayed = function () {
        return $popup.attr("data-popup-state") == "open";
    }

    this.setPopUpDisplayed = function (open) {
        $popup.attr("data-popup-state", open ? "open" : "closed");
    }

    var $panel = jQuery(cocktail.instantiate("cocktail.html.SmallScreenPopUp.popupPanel-" + this.id))
        .appendTo($popup);

    $panel.find(".popup_close_button").on("click", function () {
        $popup[0].setPopUpDisplayed(false);
    });

    var $button = jQuery(cocktail.instantiate("cocktail.html.SmallScreenPopUp.popupButton-" + this.id))
        .appendTo($popup)
        .on("click", function () {
            $popup[0].setPopUpDisplayed(true);
        });
});

