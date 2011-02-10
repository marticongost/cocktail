/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".SlideShow", function ($slideShow) {
 
    var current = null;
    var autoplayTimer = null;

    this.getAutoPlay = function () {
        return autoplayTimer != null;
    }

    this.setAutoplay = function (autoplay) {
        if (autoplay) {
            if (!autoplayTimer) {
                autoplayTimer = window.setInterval(
                    function () {                         
                        $slideShow.get(0).selectNextSlide();                         
                    },
                    this.interval
                );                
            }
        }
        else {        
            if (autoplayTimer) {
                clearInterval(autoplayTimer);
            }
        }
    }

    this.getCurrentSlide = function () {
        return current;
    }

    this.getNextSlide = function () {
        
        var $slides = $slideShow.find(this.slidesSelector);

        if (current) {
            var index = $slides.index(current);
            if (index != -1 && index + 1 < $slides.length) {
                return $slides.get(index + 1);
            }
        }

        return $slides.get(0);
    }

    this.selectNextSlide = function () {        
        this.selectSlide(this.getNextSlide());
    }

    this.selectSlide = function (slide) {
        
        if (current) {
            this._hideSlide(current);
        }
        
        var previous = current;    
        current = slide;
        
        if (slide) {
            this._showSlide(slide);
        }
        
        $slideShow.trigger("slideSelected", {
            previous: previous,
            current: slide
        });
    }
    
    this._hideSlide = function (slide) {
        jQuery(slide)
            .css({
                "position": "absolute",
                "top": 0,
                "left": 0
            })
            .fadeOut(this.transitionDuration);
    }

    this._showSlide = function (slide) {
        jQuery(slide)
            .css({"position": "static"})
            .fadeIn(this.transitionDuration);
    }

    $slideShow.css({"position": "relative"});

    // Hide all slides except the first one
    var $slides = $slideShow.find(this.slidesSelector);
    $slides.filter(":not(:first-child)")
        .css({"position": "absolute"})
        .hide();

    current = $slides.get(0);

    // Check the element's configuration to determine wether to start in
    // autoplay mode
    this.setAutoplay(this.autoplay);   
});

