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

    var $controls = jQuery(cocktail.instantiate("cocktail.html.CompoundDateSelector-" + this.id + ".controls"))
        .appendTo(this);

    // Update the value of the hidden textbox when a value is chosen in the
    // month/year dropdown selectors
    $controls.find("select").change(function () {
        var day = $controls.find(".day_selector").val();
        var month = $controls.find(".month_selector").val();
        var year = $controls.find(".year_selector").val();

        if (day && month && year) {
            var dateString = dateFormat;
            var dateString = dateString.replace(/%d/, day);
            var dateString = dateString.replace(/%m/, month);
            var dateString = dateString.replace(/%Y/, year);
        }
        else {
            var dateString = "";
        }

        $textBox.val(dateString);
    });

    // If the selector has a value pre-selected, update the dropdown selectors
    // accordingly
    var value = $textBox.val();

    if (value) {

        var parts = ["day", "month", "year"];
        var pos = {
            day: dateFormat.indexOf("%d"),
            month: dateFormat.indexOf("%m"),
            year: dateFormat.indexOf("%Y")
        }
        parts.sort(function (a, b) { return pos[a] - pos[b]; });;

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
                var part = parts[i];
                var num = String(numbers[i]);
                if (num.length < 2) {
                    num = "0" + num;
                }
                $controls.find("." + part + "_selector option[value=" + num + "]")
                    .attr("selected", "selected");
            }
        }
    }

});

