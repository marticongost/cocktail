/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2012
-----------------------------------------------------------------------------*/

cocktail.bind(".CompoundDateSelector", function ($selector) {

    var dateFormat = this.dateFormat;

    var $textBox = $selector.find("input")
        .hide();

    var $controls = jQuery(cocktail.instantiate("cocktail.html.CompoundDateSelector.controls"))
        .appendTo(this);

    // Update the value of the hidden textbox when a value is chosen in the
    // month/year dropdown selectors        
    $controls.find("select").change(function () {
        var dateString = dateFormat;
        var dateString = dateString.replace(/%d/, $controls.find(".day_selector").val());
        var dateString = dateString.replace(/%m/, $controls.find(".month_selector").val());
        var dateString = dateString.replace(/%Y/, $controls.find(".year_selector").val());
        $textBox.val(dateString);
    });

    // If the selector has a value pre-selected, update the dropdown selectors
    // accordingly
    var value = $textBox.val();

    if (value) {

        var parts = [];
        var partMap = {d: 'day', 'm': 'month', 'Y': 'year'};

        for (var i = 0; i < dateFormat.length; i++) {
            var part = partMap[dateFormat.charAt(i)];
            if (part) {
                parts.push(part);
            }
        }

        var numbers = [];
        var num = "";

        for (var i = 0; i < value.length; i++) {
            var c = value.charAt(i);
            if (c >= '1' && c <= '9' || (c == '0' && num)) {
                num += c;
            }
            else {
                if (num) {
                    numbers.push(num);
                }
                num = "";
            }
        }

        if (num) {
            numbers.push(num);
        }

        if (parts.length == numbers.length) {
            for (var i = 0; i < parts.length; i++) {
                $controls.find("." + parts[i] + "_selector option[value=" + numbers[i] + "]")
                    .attr("selected", "selected");
            }
        }
    }

});

