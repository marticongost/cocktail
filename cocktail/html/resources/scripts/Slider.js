/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".Slider", function ($slider) {

    var ALIGN_LEFT = -1;
    var ALIGN_CENTER = 0;
    var ALIGN_RIGHT = 1;

    var animationsEnabled = false;

    $slider.css("position", "relative");
    
    var $sliderFrame = $slider.find(".slider_frame");
    $sliderFrame.css("overflow", "hidden");

    var $slidesContainer = $slider.find(".slides");
    $slidesContainer.css({
        "width": "10000em",
        "position": "relative"
    });

    $slidesContainer.children()
        .attr("tabindex", "0")
        .focus(function () { $slider.get(0).centerScroll(this); })
        .keydown(function (e) {
            if (e.keyCode == 37) { 
                (jQuery(this).prev().get(0) || $slidesContainer.children().last().get(0)).focus();
                return false;
            }
            else if (e.keyCode == 39) {
                (jQuery(this).next().get(0) || $slidesContainer.children().first().get(0)).focus();
                return false;
            }
            else if (e.keyCode == 35) {
                $slidesContainer.children().last().focus();
                return false;
            }
            else if (e.keyCode == 36) {
                $slidesContainer.children().first().focus();
                return false;
            }
        });

    var $nextButton = jQuery(cocktail.instantiate("cocktail.html.Slider.nextButton"))
        .click(function () { $slider.get(0).scrollForward(); })
        .prependTo($slider);

    var $previousButton = jQuery(cocktail.instantiate("cocktail.html.Slider.previousButton"))
        .click(function () { $slider.get(0).scrollBackwards(); })
        .prependTo($slider);

    this.scrollForward = function (wrap) {

        var width = $sliderFrame.get(0).offsetWidth;
        var frameEnd = this.getScroll() + width;
        var moved = false;
        
        $slidesContainer.children().each(function () {            
            if (this.offsetLeft > frameEnd) {
                $slider.get(0).centerScroll(this, ALIGN_RIGHT);
                moved = true;
                return false;
            }
        });

        if (!moved && (wrap || wrap === undefined && this.wrap)) {
            this.setScroll(0);
        }
    }

    this.scrollBackwards = function (wrap) {
        
        var frameStart = this.getScroll();
        var moved = false;
        
        $slidesContainer.children().reverse().each(function () {
            if (this.offsetLeft < frameStart) {
                $slider.get(0).centerScroll(this, ALIGN_LEFT);
                moved = true;
                return false;
            }
        });

        if (!moved && (wrap || wrap === undefined && this.wrap)) {
            this.centerScroll($slidesContainer.children().last().get(0));
        }
    }

    this.centerScroll = function (slide, alignment) {

        if (!this.hasOverflow()) {
            this.setScroll(0);
            return;
        }

        var width = $sliderFrame.get(0).offsetWidth;
        var contentWidth = this._getContentWidth();

        if (alignment == ALIGN_CENTER || alignment === undefined) {
            var scroll = Math.max(0, slide.offsetLeft + slide.offsetWidth / 2 - width / 2);
            scroll = Math.min(scroll, contentWidth - width);            
        }
        else if (alignment == ALIGN_RIGHT) {
            var scroll = Math.max(0, slide.offsetLeft + slide.offsetWidth - width);
        }
        else if (alignment == ALIGN_LEFT) {
            var scroll = slide.offsetLeft;
            scroll = Math.min(scroll, contentWidth - width);
        }

        this.setScroll(scroll);
    }

    this.getScroll = function () {
        return -$slidesContainer.get(0).offsetLeft;
    }

    this.setScroll = function (scroll) {
        if (animationsEnabled) {
            $slidesContainer.animate({left: -scroll}, this.transitionDuration);
        }
        else {
            $slidesContainer.get(0).style.left = -scroll + "px";
        }
    }

    this._centerSelected = function () {
        var $selected = $slidesContainer.children(".selected");
        if ($selected.length) {
            this.centerScroll($selected.get(0));
        }
    }

    this.hasOverflow = function () {
        return this._getContentWidth() > $sliderFrame.get(0).offsetWidth;
    }

    this._getContentWidth = function () {
        var last = $slidesContainer.children().last().get(0);
        if (!last) {
            return 0;
        }
        return last.offsetLeft + last.offsetWidth;
    }

    this.getAnimationsEnabled = function () {
        return animationsEnabled;
    }

    this.setAnimationsEnabled = function (value) {
        animationsEnabled = value;
    }

    this._centerSelected();

    $slidesContainer.find("img").load(function () {
        var prevAnimationsEnabled = animationsEnabled;
        animationsEnabled = false
        var slider = $slider.get(0);
        slider._centerSelected();
        slider.contentChanged();
        animationsEnabled = prevAnimationsEnabled;
    });

    this.contentChanged = function () {
        if (this.hasOverflow()) {
            $slider.removeClass("no_overflow");
            $slider.addClass("has_overflow");
        }
        else {
            $slider.removeClass("has_overflow");
            $slider.addClass("no_overflow");
        }
    }

    animationsEnabled = true;
    this.contentChanged();
});

