
cocktail.bind("form", function ($form) {

    // Hidden fields
    var params = {};
    var paramInputs = null;
    var volatileParams = {};
    
    // Additional form parameters (NOTE: since it requires javascript, code
    // shouldn't depend on parameters set with these methods - it's only
    // meant for optional, non critical parameters).
    this.getParameter = function (name) {
        return params[name];
    }

    this.setParameter = function (name, value, isVolatile /* = false */) {
        params[name] = value;
        volatileParams[name] = isVolatile;
    }

    $form.submit(function () {

        // Remove inputs for previous submit operations
        if (paramInputs) {
            for (var i = 0; i < paramInputs.length; i++) {
                this.removeChild(paramInputs[i]);
            }
        }
        
        // Add hidden fields with the additional parameters defined by the form
        paramInputs = [];

        for (var name in params) {
            var value = params[name];
            if (value !== undefined) {
                var input = cocktail.createElement("input", name, "hidden");
                input.value = value;
                paramInputs.push(input);
                this.appendChild(input);
            
                // Remove volatile parameters (they will still be submitted in
                // the current submit event, but not if the form is
                // submitted again).
                if (volatileParams[name]) {
                    delete params[name];
                    delete volatileParams[name];
                }
            }
        }
    });
});

// Fix <button> tags in IE < 9
if (jQuery.browser.msie && Number(jQuery.browser.version) < 9) {

    cocktail.bind("form", function ($form) {

        var hidden;

        this.setSubmitButtonForIE = function (name, value) {
            clearHidden();
            hidden = document.createElement("<input type='hidden' name='" + name + "'>");
            hidden.value = value;
            this.appendChild(hidden);
            $form.submit();
        }

        function clearHidden() {
            if (hidden) {
                $form.remove(hidden);
            }
        }

        $form.find("input[type=submit]").live("click", clearHidden);
    });

    cocktail.bind("button[type=submit]", function ($button) {
        if (this.parentNode) {
            var replacement = document.createElement("<button type='button'>");
            replacement.isButtonReplacement = true;
            replacement.buttonName = this.name;
            var attribute = this.attributes.getNamedItem("value");
            replacement.buttonValue = attribute ? attribute.nodeValue : "";
            replacement.id = this.id;
            replacement.title = this.title;
            replacement.className = this.className;
            replacement.innerHTML = this.innerHTML;
            replacement.style.cssText = this.style.cssText;
            // FIXME: this is woost specific code and doesn't belong here
            replacement.minSelection = this.minSelection;
            replacement.maxSelection = this.maxSelection;

            jQuery(replacement).click(function () {
                jQuery(replacement).closest("form").each(function () {
                    this.setSubmitButtonForIE(replacement.buttonName, replacement.buttonValue);                    
                });
            });
            $button.replaceWith(replacement);
        }
    });
}

