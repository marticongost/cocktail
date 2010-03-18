cocktail.init(function (root) {

    jQuery("form", root).each(function () {

        if (this.__formScript) {
            return;
        }

        this.__formScript = true;

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

        jQuery(this).submit(function () {

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

        // Fix <button> tags in IE
        if (jQuery.browser.msie) {

            var form = this;
            var hidden;

            function clearHidden() {
                if (hidden) {
                    form.removeChild(hidden);
                }
            }

            jQuery(this).click(function (e) {

                var ele = (e.target || e.srcElement);

                if (ele.tagName == "BUTTON" && ele.isButtonReplacement && !ele.disabled) {
                    clearHidden();
                    hidden = document.createElement("<input type='hidden' name='" + ele.buttonName + "'>");
                    hidden.value = ele.buttonValue;             
                    jQuery(form).append(hidden);
                    jQuery(form).submit();                   
                }
                else if (ele.tagName.toLowerCase() == "input" && ele.type == "submit") {
                    clearHidden();
                }

            });

            jQuery("button[type=submit]", this).each(function () {
                if (this.parentNode) {
                    var replacement = document.createElement("<button type='button'>");
                    replacement.isButtonReplacement = true;
                    replacement.buttonName = this.name;
                    var attribute = this.attributes.getNamedItem("value");
                    replacement.buttonValue = attribute ? attribute.nodeValue : "";
                    replacement.id = this.id;
                    replacement.className = this.className;
                    replacement.innerHTML = this.innerHTML;
                    replacement.style.cssText = this.style.cssText;
                    replacement.minSelection = this.minSelection;
                    replacement.maxSelection = this.maxSelection;
                    jQuery(this).replaceWith(replacement);
                }
            });
        }
    });
});

