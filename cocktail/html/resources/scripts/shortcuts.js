/*-----------------------------------------------------------------------------
Highlighting and invocation of keyboard shortcuts.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
-----------------------------------------------------------------------------*/

cocktail.setShortcut = function (element, key, target /* optional */) {

    var expr = new RegExp(key, "i");
    var lowerCaseKey = key.toLowerCase();

    for (var i = 0; i < element.childNodes.length; i++) {

        var node = element.childNodes[i];

        if (node.nodeType == 3) {
            var text = node.nodeValue;

            if (text.match(expr)) {

                var pos = text.toLowerCase().indexOf(lowerCaseKey);

                element.insertBefore(
                    document.createTextNode(text.substring(0, pos)),
                    node
                );

                var shortcutHighlight = document.createElement('u');
                shortcutHighlight.className = "shortcut";
                shortcutHighlight.appendChild(document.createTextNode(text.charAt(pos)));
                element.insertBefore(shortcutHighlight, node);

                element.insertBefore(
                    document.createTextNode(text.substring(pos + 1)),
                    node
                );

                element.removeChild(node);
                break;
            }
        }
    }

    element.title = "Alt+Shift+" + key.toUpperCase();

    jQuery(document).bind(
        'keydown',
        {
            combi: 'Alt+Shift+' + lowerCaseKey,
            disableInInput: false
        },
        function (evt) {
            jQuery(target || element).click();
            return false;
        }
    );
}

