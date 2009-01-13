jQuery(document).ready( function () {
    
    var button_names = [];
    
    jQuery(".Form button").each( function () {
        var name = jQuery(this).attr('name');
        if(button_names.indexOf(name) < 0) {
            var replaced = document.createElement('input');
            var class_name =  'replaced-' + jQuery(this).attr('id');           
            replaced.className = class_name;        
            jQuery(replaced).attr({
                type: "hidden",
                name: name
            }).insertBefore(jQuery(this));             
            button_names.push(name);
        }
        jQuery(this).removeAttr('name');
        jQuery(this).click( function () {
            jQuery(replaced).val(jQuery(this).val());
        });
    });
    
});