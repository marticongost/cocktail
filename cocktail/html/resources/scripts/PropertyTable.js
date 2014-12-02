/*-----------------------------------------------------------------------------


@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
-----------------------------------------------------------------------------*/

cocktail.bind(".PropertyTable", function ($ptable) {

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

    $ptable.find(".type_group").each(function () {
        
        this.collapsedCookieKey = "cocktail.html.PropertyTable-collapsed " + this.groupSchema;
        setCollapsed.call(this, jQuery.cookie(this.collapsedCookieKey) == "true");
            
        jQuery(this).find(".type_header").click(function () {
            var group = jQuery(this).parents(".type_group").get(0);
            toggleCollapsed.call(group);
        });
    });
});

