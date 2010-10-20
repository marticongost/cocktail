/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
-----------------------------------------------------------------------------*/

cocktail.bind(".DatePicker", function ($datePicker) {

    var timeBox;

    if (this.hasDate) {

        // Apply the date picker behavior
        var params = $.extend(
            {},
            $.datepicker.regional[cocktail.getLanguage()],
            this.datePickerParams
        );
        $datePicker.datepicker(params);

        // Create the time portion of date time controls
        if (this.hasTime) {
            timeBox = document.createElement('input');
            this.timeBox = timeBox;
            timeBox.className = "time";
            timeBox.setAttribute('type', 'text');

            if (this.value != "") {
                var parts = this.value.split(" ");
                this.value = parts[0];
                timeBox.value = parts[1];
            }

            $datePicker.after(timeBox);
        }
    }
    else if (this.hasTime) {
        var timeBox = this;
    }

    // Masked input for time boxes
    if (timeBox) {
        jQuery(timeBox).mask("99:99:99", {fullfilled: true, maskedtype: "time"});
    }
});

// When submitting forms with date time fields, put the date and time
// parts back together
cocktail.bind("form", function ($form) {
    $form.submit(function () {
        $form.find(".DatePicker").each(function () {
            if (this.hasDate && this.hasTime) {
                this.value = this.value + " " + this.timeBox.value;
            }
        });
    });
});

