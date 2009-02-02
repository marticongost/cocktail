/*-----------------------------------------------------------------------------
Highlighting and invocation of keyboard shortcuts.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
-----------------------------------------------------------------------------*/

cocktail.setShortcut = function (element, key) {

    if (!jQuery(element).is("button")) {
        element = jQuery(".label", element);
    }
    
    var expr = new RegExp(key, "i");
    var lowerCaseKey = key.toLowerCase();

    jQuery("[nodeType=3]", element).each(function () {
        
        var text = this.nodeValue;
            
        if (text.match(expr)) {
            
            var pos = text.toLowerCase().indexOf(lowerCaseKey);

            var wrapper = document.createElement('span');
            wrapper.appendChild(document.createTextNode(text.substring(0, pos)));
            
            var shortcutHighlight = document.createElement('span');
            shortcutHighlight.className = "shortcut";
            shortcutHighlight.appendChild(document.createTextNode(text.charAt(pos)));
            wrapper.appendChild(shortcutHighlight);
            
            wrapper.appendChild(document.createTextNode(text.substring(pos + 1)));
            
            jQuery(this).replaceWith(wrapper);
        }
    });                                             

    element.title = "Alt+Shift+" + key.toUpperCase();
    
    jQuery(document).bind(
        'keydown',
        {
            combi:'Alt+Shift+' + lowerCaseKey,
            disableInInput: false
        },
        function (evt) {
            element.click();
            return false; 
        }
    );
}

