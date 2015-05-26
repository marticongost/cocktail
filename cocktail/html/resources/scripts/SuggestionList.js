/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         May 2015
-----------------------------------------------------------------------------*/

cocktail.bind(".SuggestionList", function ($control) {

    var $customDisplay = $control.find(".custom_value_display");
    var $selector = jQuery(cocktail.instantiate("cocktail.html.SuggestionList.suggestionsSelector"));
    $selector.insertBefore($customDisplay);
    $selector.children().last().append($customDisplay);

    if ($customDisplay.is("input, select, textarea")) {
        var $customInput = $customDisplay;
    }
    else {
        var $customInput = $customDisplay.find("input, select, textarea");
    }

    var name = $customInput.attr("name");
    $customInput.attr("name", name + "-custom_value");

    var $hidden = jQuery("<input type='hidden'>")
        .attr("name", name)
        .appendTo($control);

    var $options = $selector.find("[name='" + name + "-suggestion']");
    var lastOption = $options.last()[0];
    $options.click(function () {
            if (this == lastOption) {
                $customInput
                    .removeAttr("disabled")
                    .focus();
                $hidden.val($customInput.val());
            }
            else {
                $customInput.attr("disabled", "disabled");
                $hidden.val(this.value);
            }
        });

    $customInput.change(function () {
        $hidden.val($customInput.val());
    });

    // Initialization
    var value = $customInput.val();
    var usingSuggestedValue = false;
    $options.each(function () {
        if (this != lastOption) {
            if (this.value == value) {
                usingSuggestedValue = true;
                this.checked = true;
                return false;
            }
        }
    });

    if (!usingSuggestedValue && value) {
        lastOption.checked = true;
    }
    else {
        $customInput
            .val("")
            .attr("disabled", "disabled");
    }

    $hidden.val(value);
});

