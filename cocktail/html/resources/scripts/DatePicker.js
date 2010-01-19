/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {

    jQuery(".DatePicker", root).each(function () {

        var timeBox;

        if (this.hasDate) {

            // Apply the date picker behavior
            var params = $.extend(
                {},
                $.datepicker.regional[cocktail.getLanguage()],
                this.datePickerParams
            );
            jQuery(this).datepicker(params);

            // Create the time portion of date time controls
            if (this.hasTime) {
                var timeBox = document.createElement('input');
                this.timeBox = timeBox;
                timeBox.className = "time";
                timeBox.setAttribute('type', 'text');
                timeBox.name = "timepickr_" + this.name;

                if (this.value != "") {
                    var parts = this.value.split(" ");
                    this.value = parts[0];
                    timeBox.value = parts[1];
                }

                jQuery(this).after(timeBox);
            }
        }
        else if (this.hasTime) {
            var timeBox = this;
        }

        // Masked input for time boxes
        if (timeBox) {
            jQuery(timeBox).mask("99:99:99", {fullfilled: true, maskedtype: "time"});
        }

        // When submitting forms with date time fields, put the date and time
        // parts back together
        if (this.hasDate && this.hasTime) {

            // Make sure this event is only declared once
            if (!cocktail.__DatePicker_formEvent) {
                cocktail.__DatePicker_formEvent = true;
                
                jQuery("form").submit( function () {
                    jQuery(".DatePicker", this).each(function () {
                        if (this.hasTime) {
                            this.value = this.value + " " + this.timeBox.value;
                        }
                        jQuery(this.timeBox).removeAttr('name');
                    });
                });
            }
        }
    });
});

