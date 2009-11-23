cocktail.init(function (root) {

    if (jQuery.browser.msie) {

        jQuery("form", root).each(function () {

			if (this.buttonsReplacementScript) {
				return;
			}

			this.buttonsReplacementScript = true;

            var form = this;
            var hidden;

            function clearHidden() {
                if (hidden) {
                    form.removeChild(hidden);
                }
            }

			jQuery(form).click(function (e) {

				var element = e.srcElement;

				if (element.isButtonReplacement) {
                    clearHidden();
                    hidden = document.createElement("<input type='hidden' name='" + element.buttonName + "'>");
                    hidden.value = element.buttonValue;
					jQuery(form).append(hidden);
                    jQuery(form).submit();
				}
				else if (element.tagName.toLowerCase() == "input" && element.type == "submit") {
					clearHidden();
				}
			});
        });
    }
});

cocktail.init(function (root) {
	if (jQuery.browser.msie) {
		jQuery("button[type=submit]", root).each(function () {
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
				jQuery(this).replaceWith(replacement);
			}
		});
	}
});

