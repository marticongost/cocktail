/*-----------------------------------------------------------------------------


@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
-----------------------------------------------------------------------------*/

cocktail.init(function (root) {
    
    function setCollapsed(collapsed) {
        
        this.collapsed = collapsed;
        jQuery.cookie(this.collapsedCookieKey, collapsed ? "true" : "false");
        
        if (collapsed) {
            jQuery(this).addClass("collapsed");
        }
        else {
            jQuery(this).removeClass("collapsed");
        }
    }

    function toggleCollapsed() {
        setCollapsed.call(this, !this.collapsed);
    }

    jQuery(".PropertyTable", root).each(function () {

        jQuery(this).addClass("scripted");

        jQuery(".type_group", this).each(function () {
            
            this.collapsedCookieKey = "cocktail.html.PropertyTable-collapsed " + this.groupSchema;
            setCollapsed.call(this, jQuery.cookie(this.collapsedCookieKey) == "true");
                
            jQuery(".type_header", this).click(function () {
                var group = jQuery(this).parents(".type_group").get(0);
                toggleCollapsed.call(group);
            });
        });
    });
});

