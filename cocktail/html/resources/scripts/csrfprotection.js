/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         October 2016
-----------------------------------------------------------------------------*/

(function () {

    // Obtain the token from the cookie sent by the server
    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }

    cocktail.csrfprotection.token = getCookie(cocktail.csrfprotection.cookieName);
})();

// Method to decorate XHR objects
cocktail.csrfprotection.setupRequest = function (xhr) {
    xhr.setRequestHeader(
        cocktail.csrfprotection.header,
        cocktail.csrfprotection.token
    );
}

// Inject a header with the token into all Ajax requests
// (only works on requests made through the jQuery API)
if (window.jQuery) {
    jQuery.ajaxPrefilter(function (options, originalOptions, xhr) {
        cocktail.csrfprotection.setupRequest(xhr);
    });
}

if (!cocktail.bind) {
    cocktail._selectors = [];
    cocktail.bind = function (selector, initializer) {
        cocktail._selectors.push([selector, initializer]);
    }
    window.addEventListener("DOMContentLoaded", function () {
        for (var s = 0; s < cocktail._selectors.length; s++) {
            var selector = cocktail._selectors[s][0];
            var initializer = cocktail._selectors[s][1];
            var elements = document.querySelectorAll(selector);
            for (var i = 0; i < elements.length; i++) {
                initializer.call(elements[i]);
            }
        }
    });
}

// Inject the token into posted forms. Take care of the formmethod attribute!
cocktail.bind("[formmethod]", function () {
    this.addEventListener("click", function (e) {
        var node = this;
        while (node) {
            if (node.tagName == "FORM") {
                node._cocktailFormMethod = this.getAttribute("formmethod");
                break;
            }
            node = node.parentNode;
        }
    });
});

cocktail.bind("form", function () {
    this.addEventListener("submit", function (e) {
        var method = this._cocktailFormMethod || this.method;
        if (method) {
            method = method.toUpperCase();
            if (method == "POST" || method == "PUT" || method == "DELETE") {
                if (!this.querySelector("[name='" + cocktail.csrfprotection.field + "']")) {
                    var hidden = document.createElement("input");
                    hidden.type = "hidden";
                    hidden.name = cocktail.csrfprotection.field;
                    hidden.value = cocktail.csrfprotection.token;
                    this.append(hidden);
                }
            }
        }
        this._cocktailFormMethod = null;
    });
});

