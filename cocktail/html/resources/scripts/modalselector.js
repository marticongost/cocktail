/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {
    
    var PREFIX = "cocktail.html.modal_selector ";

    jQuery(".modal_selector", root).each(function () {

        // Create a dialog for the check list
        var dialog = document.createElement("div");
        dialog.className = "modal_selector_dialog";
        
        var dialogContainer = document.createElement("div");
        dialogContainer.className = "container";
        dialog.appendChild(dialogContainer);

        // Dialog buttons
        var buttons = document.createElement("div");
        buttons.className = "buttons";
        dialog.appendChild(buttons);
        
        var acceptButton = document.createElement("input");
        acceptButton.className = "accept";
        acceptButton.type = "button";
        acceptButton.value = cocktail.translate(PREFIX + "accept button");
        buttons.appendChild(acceptButton);
        jQuery(acceptButton).click(function () {
            showSelection();
            cocktail.closeDialog();
        });

        var cancelButton = document.createElement("input");
        cancelButton.className = "cancel";
        cancelButton.type = "button";
        cancelButton.value = cocktail.translate(PREFIX + "cancel button");
        buttons.appendChild(cancelButton);
        jQuery(cancelButton).click(cocktail.closeDialog);

        // Selection
        var selector = document.createElement("div");
        selector.className = "modal_selector_control";
        
        jQuery(this).replaceWith(selector);        
        jQuery(dialog).hide();
        selector.appendChild(dialog);
        dialogContainer.appendChild(this);

        var container = document.createElement("div");
        container.className = "container";
        selector.appendChild(container);

        function showSelection() {
            jQuery(container).empty();
            jQuery("input[type=checkbox]:checked", dialog).each(function () {
                
                var content = jQuery("label", this.parentNode).get(0);
                var entry = document.createElement("div");
                entry.className = "entry " + content.className;
                entry.innerHTML = content.innerHTML;

                if (!this.disabled) {
                    var input = document.createElement("input");
                    input.type = "hidden";
                    input.name = this.name;
                    input.value = this.value;
                    entry.appendChild(input);
                }

                container.appendChild(entry);
            });
        }

        showSelection();

        var button = document.createElement("input");
        button.type = "button";
        button.className = "select";
        button.value = cocktail.translate(PREFIX + "select button");
        selector.appendChild(button);
        jQuery(button).click(function () {
            jQuery(dialog).show();
            cocktail.showDialog(dialog);
        });   
    });
});

