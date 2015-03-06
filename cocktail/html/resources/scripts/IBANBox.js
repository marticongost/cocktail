/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2014
-----------------------------------------------------------------------------*/

cocktail.bind(".IBANBox", function ($box) {

    var currentFormat = null;

    function updateMask() {

        var value = $box.val();
        var format = null;

        if (value.length >= 2) {
            var country = value.substr(0, 2).toUpperCase();
            var IBANLength = $box.get(0).lengthByCountry[country];
            if (IBANLength) {
                format = "AA99";
                for (var i = 4; i < IBANLength; i++) {
                    if (i % 4 == 0) {
                        format += "-";
                    }
                    format += "#";
                }
            }
        }

        if (format) {
            if (format != currentFormat) {
                $box.inputmask(format, {
                    definitions: {
                        'A': {
                            validator: "[A-Za-z]",
                            cardinality: 1,
                            casing: "upper"
                        },
                        '#': {
                            validator: "[A-Za-z\u0410-\u044F\u0401\u04510-9]",
                            cardinality: 1,
                            casing: "upper"
                        },
                        '9': jQuery.inputmask.defaults['9']
                    }
                });
            }
        }
        else {
            if (currentFormat) {
                $box.inputmask("remove");
            }
        }

        currentFormat = format;
    }

    $box.keyup(updateMask);
    $box.change(updateMask);
    updateMask();
});

