jQuery(document).ready( function () {
    
    var button_names = [];
    
    jQuery("form button").each( function () {
        var name = jQuery(this).attr('name');        
        if(button_names.indexOf(name) < 0) {
            var replaced = document.createElement('input');       
            jQuery(replaced).attr({
                type: "hidden",
                name: name
            }).insertBefore(jQuery(this));             
            button_names.push(name);
        }
        jQuery(this).removeAttr('name');        
        jQuery(this).click( function () {          
            jQuery("input[name='" + name + "']").val(jQuery(this).val());
        });
    });
    
});