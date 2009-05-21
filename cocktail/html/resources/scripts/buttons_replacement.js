cocktail.init(function () {
    
    if (!Array.prototype.indexOf)
    {
      Array.prototype.indexOf = function(elt /*, from*/)
      {
        var len = this.length;
    
        var from = Number(arguments[1]) || 0;
        from = (from < 0)
             ? Math.ceil(from)
             : Math.floor(from);
        if (from < 0)
          from += len;
    
        for (; from < len; from++)
        {
          if (from in this &&
              this[from] === elt)
            return from;
        }
        return -1;
      };
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

        if(this.attributes.getNamedItem("value")){
            jQuery(this).click( function () {                
                jQuery("input[name='" + nom + "']").val(this.attributes.getNamedItem("value").nodeValue);
            });
        }
        
    });
        
    if(jQuery.browser.msie){                    
        jQuery(".body form").submit( function () {

            jQuery(this).find("button[type='submit']:visible").each(function () {
                //alert(jQuery(this).html());
                var clases = jQuery(this).attr('class');                
                var boto = document.createElement('button');
                boto.innerHTML = jQuery(this).html();
                if(jQuery(this).attr('class') != "")  boto.className = jQuery(this).attr('class');
                //var button = document.createElement("<button class='" + clases + "' type='button'>" + jQuery(this).html() + "</button>");
                jQuery(this).after(boto).remove();
            });

            return true;
        });
    }
});
