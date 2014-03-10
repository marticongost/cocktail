/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2010
-----------------------------------------------------------------------------*/

cocktail.bind(".TextSizeBar", function ($textSizeBar) {
 
    function setDisabled($control, disabled) {
        if (disabled) {
            $control.attr("disabled", true);
        }
        else {
            $control.removeAttr("disabled");
        }
    }
        
    this.setTextSize = function (newSize) {
        
        if (!isNaN(this.minTextSize) && newSize < this.minTextSize) {
            newSize = this.minTextSize;
        }        
        else if (!isNaN(this.maxTextSize) && newSize > this.maxTextSize) {
            newSize = this.maxTextSize;
        }

        jQuery(document.body).removeClass("text_size-" + this.textSize);
        this.textSize = newSize;
        jQuery.cookie(this.textSizeCookie, newSize, {path: "/"});
        jQuery(document.body)
            .css("font-size", (100 + newSize * 10) + "%")
            .addClass("text_size-" + newSize);
        
        setDisabled(
            $textSizeBar.find(".decrease_size_button"),
            !isNaN(this.minTextSize) && newSize <= this.minTextSize
        )
            
        setDisabled(
            $textSizeBar.find(".increase_size_button"),
            !isNaN(this.maxTextSize) && newSize >= this.maxTextSize
        )        
    }

    this.changeTextSize = function (change) {
        this.setTextSize(this.textSize + change);
    }

    $textSizeBar.find(".decrease_size_button").click(function (e) {
        $textSizeBar.get(0).changeTextSize(-1);
        e.preventDefault();
    });

    $textSizeBar.find(".increase_size_button").click(function (e) {
        $textSizeBar.get(0).changeTextSize(1);
        e.preventDefault();
    });
});

