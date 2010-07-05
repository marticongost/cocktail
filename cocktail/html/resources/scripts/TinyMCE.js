/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2010
-----------------------------------------------------------------------------*/

(function () {

    // Delay the initialization of TinyMCE instances until all page assets are
    // loaded (it doesn't work otherwise)
    var documentLoaded = false;
    
    jQuery(window).bind("load", function () {
        documentLoaded = true;
        jQuery(".TinyMCE").each(function () {
            tinyMCE.init(this.tinymceSettings);
        });
    });

    cocktail.bind(".TinyMCE", function () {
        if (documentLoaded) {
            tinyMCE.init(this.tinymceSettings);
        }
    });
})();

