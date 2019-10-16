/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         February 2016
-----------------------------------------------------------------------------*/

cocktail.bind(".RatingBox", function ($box) {

    var $numberBox = $box.find(".number_box");

    var $hidden = jQuery("<input type='hidden'>")
        .attr("name", $numberBox.attr("name"));

    $numberBox.replaceWith($hidden);

    var $starsList = jQuery(cocktail.instantiate("cocktail.html.RatingBox.stars-" + this.id))
        .appendTo($box);

    var $stars = $starsList.find(".star");
    var $buttons = $stars.find(".star_button");

    this.getValue = function () {
        return Number($hidden.val());
    }

    this.setValue = function (value) {
        $hidden.val(value);
        $stars.each(function () {
            var $star = jQuery(this);
            var starValue = Number($star.data("star-value"));
            if (starValue < value) {
                $star.attr("data-star-state", "lower");
            }
            else if (starValue == value) {
                $star.attr("data-star-state", "equal");
            }
            else {
                $star.attr("data-star-state", "higher");
            }
        });
    }

    this.getDisabled = function () {
        return $box.attr("data-disabled") == "true";
    }

    this.setDisabled = function (disabled) {
        if (disabled) {
            $box.attr("data-disabled", "true");
            $buttons.attr("disabled", "disabled");
        }
        else {
            $box.attr("data-disabled", "false");
            $buttons.removeAttr("disabled");
        }
    }

    $stars.on("click", ".star_button", function () {
        var $star = jQuery(this).closest(".star");
        var oldValue = $box[0].getValue();
        var newValue = Number($star.data("star-value"));
        var changed = (oldValue != newValue);
        $box[0].setValue(newValue);
        if (changed) {
            $box.trigger("change");
        }
    });

    var initialValue = Number($numberBox.val());
    if (!isNaN(initialValue)) {
        this.setValue(initialValue);
    }

    this.setDisabled(this.getDisabled());
});

