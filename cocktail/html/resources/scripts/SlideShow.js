/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".SlideShow", function ($slideShow) {
 
    var current = null;
    var autoplayTimer = null;

    // Create navigation controls
    if (this.navigationControls) {
        jQuery(cocktail.instantiate("cocktail.html.SlideShow.previousSlideButton"))
            .appendTo($slideShow)
            .click(function () { $slideShow.get(0).selectPreviousSlide(); });
    
        jQuery(cocktail.instantiate("cocktail.html.SlideShow.nextSlideButton"))
            .appendTo($slideShow)
            .click(function () { $slideShow.get(0).selectNextSlide(); });
    }

    this.getAutoPlay = function () {
        return autoplayTimer != null;
    }

    this.stop = function () {
        if (autoplayTimer) {
            clearInterval(autoplayTimer);
        }
    }

    this.start = function () {
        autoplayTimer = window.setInterval(
            function () {                         
                $slideShow.get(0).selectNextSlide();                         
            },
            this.interval
        );        
    }

    this.restart = function () {
        this.stop();
        this.start();
    }

    this.setAutoplay = function (autoplay) {
        if (autoplay) {
            if (!autoplayTimer) this.start();                            
        }
        else {        
            this.stop();
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

    this.getPrevSlide = function () {
        
        var $slides = $slideShow.find(this.slidesSelector);

        if (current) {
            var index = $slides.index(current);
            if (index != -1 && index - 1 > -1) {
                return $slides.get(index - 1);
            }
        }

        return $slides.get($slides.length-1);
    }
    
    this.selectNextSlide = function () {        
        this.selectSlide(this.getNextSlide());
    }

    this.selectPrevSlide = function () {        
        this.selectSlide(this.getPrevSlide());
    }

    this.selectSlide = function (slide) {

        if (typeof(slide) == "number") {
            slide = $slideShow.find(this.slidesSelector).get(slide);
        }

        if (slide == current) {
            return;
        }

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

