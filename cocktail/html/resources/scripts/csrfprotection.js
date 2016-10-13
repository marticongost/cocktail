/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         October 2016
-----------------------------------------------------------------------------*/

cocktail.declare("cocktail.csrfprotection");

jQuery(function () {

    // Obtain the token from the cookie sent by the server
    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }

    cocktail.csrfprotection.token = getCookie(cocktail.csrfprotection.cookieName);

    // Method to decorate XHR objects
    cocktail.csrfprotection.setupRequest = function (xhr) {
        xhr.setRequestHeader(
            cocktail.csrfprotection.header,
            cocktail.csrfprotection.token
        );
    }

    // Inject a header with the token into all Ajax requests
    // (only works on requests made through the jQuery API)
    jQuery.ajaxPrefilter(function (options, originalOptions, xhr) {
        cocktail.csrfprotection.setupRequest(xhr);
    });
});

// Inject the token into posted forms. Take care of the formmethod attribute!
cocktail.bind("[formmethod]", function($element) {
    $element.click(function(e) {
        jQuery(this).closest("form").data("cocktail-form-method", this.getAttribute("formmethod"));
    });
});

cocktail.bind("form", function($form) {
    $form.submit( function (e) {
        var method = $form.data("cocktail-form-method") || this.method;
        if (method && method.toUpperCase() == "POST") {
            if (!$form.find("[name='" + cocktail.csrfprotection.field + "']").length) {
                var hidden = document.createElement("input");
                hidden.type = "hidden";
                hidden.name = cocktail.csrfprotection.field;
                hidden.value = cocktail.csrfprotection.token;
                $form.append(hidden);
            }
        }
    });
});

