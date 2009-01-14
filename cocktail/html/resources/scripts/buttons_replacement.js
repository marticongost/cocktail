jQuery(document).ready( function () {
    
    if(!Array.indexOf){
	    Array.prototype.indexOf = function(obj){
	        for(var i=0; i<this.length; i++){
	            if(this[i]==obj){
	                return i;
	            }
	        }
	        return -1;
	    }
	}

    
    var button_names = [];
    
    jQuery("form button").each( function (index) {
        
        var nom, replaced
        
        if(jQuery(this).attr('name') == ""){
            nom = "joker_" + index;
        }else{
            nom = jQuery(this).attr('name');
            jQuery(this).removeAttr('name');
        }
        
        if(button_names.indexOf(nom) < 0) {
            //TODO: Retirar con el control que carga el script solo en IE.
            if(jQuery.browser.msie){                
                replaced = document.createElement("<input type='hidden' name='" + nom + "'>");
            }else{
                replaced = document.createElement('input');
                jQuery(replaced).attr({
                    type: "hidden",
                    name: nom
                });
            }            
            jQuery(replaced).insertBefore(jQuery(this));             
            button_names.push(nom);
        }
        /*            
        this.setAttribute('type','submit');                              
        var newInput = document.createElement('input');
        newInput.type = 'submit'; // that should work even with IE
        if(this.attributes.getNamedItem("value")){
            var attr = document.createAttribute("value");
            newInput.attributes.setNamedItem(attr);
        }
        //newInput.innerHTML = this.innerHTML;
        this.parentNode.replaceChild(newInput, this);
        */
        if(this.attributes.getNamedItem("value")){
            jQuery(this).click( function () {                                
                jQuery("input[name='" + nom + "']").val(this.attributes.getNamedItem("value").nodeValue);                     
            });
        }
        
    });
    
    
});