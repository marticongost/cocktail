/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2011
-----------------------------------------------------------------------------*/

cocktail.slideShowTransitions = {
    fade: {
        show: function (slideShow, slide, callback) {
            jQuery(slide).fadeIn(slideShow.transitionDuration, callback);
        },
        hide: function (slideShow, slide, callback) {
            jQuery(slide).fadeOut(slideShow.transitionDuration, callback);
        }
    },
    topBottomSlide: {
        show: function (slideShow, slide, callback) {
            jQuery(slide)
                .hide()
                .css({zIndex: 2})
                .slideDown(slideShow.transitionDuration, callback);
        },
        hide: function (slideShow, slide, callback) {
            slide.style.zIndex = 1;
            if (callback) {
                callback.call(slide);
            }
        }
    }
}

cocktail.bind(".SlideShow", function ($slideShow) {

    var current = null;
    var autoplayTimer = null;

    if (!this.transitionEffect) {
        this.transitionEffect = "fade";
    }

    // Create navigation controls
    if (this.navigationControls) {
        jQuery(cocktail.instantiate("cocktail.html.SlideShow.previousSlideButton"))
            .appendTo($slideShow)
            .click(function () { $slideShow.get(0).selectPrevSlide(); });

        jQuery(cocktail.instantiate("cocktail.html.SlideShow.nextSlideButton"))
            .appendTo($slideShow)
            .click(function () { $slideShow.get(0).selectNextSlide(); });
    }

    // Create bullets controls
    if (this.bulletControls) {

        this.selectBullet = function () {
            jQuery(".bullet",$slideShow).removeClass("selected");
            var index = $slideShow.find(this.slidesSelector).index(current);
            jQuery(jQuery(".bullet",$slideShow).get(index)).addClass("selected");
        }

        jQuery(cocktail.instantiate("cocktail.html.SlideShow.bulletSlideButtons"))
            .appendTo($slideShow);

        jQuery.each(jQuery(".bullet",$slideShow),function (index,bullet) {
            jQuery(bullet).click(function () {
                $slideShow.get(0).selectSlide(index);
            });
        });

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
                var slideShow = $slideShow.get(0);
                if (!slideShow.contentStatePreventsAutoplay()) {
                    slideShow.selectNextSlide();
                }
            },
            this.interval
        );
    }

    this.contentStatePreventsAutoplay = function () {
        return $slideShow.find(".prevent_autoplay").length > 0;
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

        $slideShow.trigger("beforeSlideChange", {
            previous: previous,
            current: slide
        });

        if (this.bulletControls) {
            $slideShow.get(0).selectBullet();
        }

        if (slide) {
            this._showSlide(slide, function () {
                $slideShow.trigger("afterSlideChange", {
                    previous: previous,
                    current: slide
                });
            });
        }

        $slideShow.trigger("slideSelected", {
            previous: previous,
            current: slide
        });
    }

    this._hideSlide = function (slide) {

        var $slide = jQuery(slide);
        $slide.parent().height($slide.parent().height());

        $slide
            .addClass("loosingFocus")
            .css({
                "position": "absolute",
                "top": 0,
                "left": 0
            });

        cocktail.slideShowTransitions[this.transitionEffect].hide(
            this,
            slide,
            function () {
                jQuery(this).removeClass("loosingFocus");
            }
        );
    }

    this._showSlide = function (slide, callback) {
        $slideShow.addClass("inTransition");

        jQuery(slide)
            .addClass("gainingFocus")
            .css({"position": "relative"});

        cocktail.slideShowTransitions[this.transitionEffect].show(
            this,
            slide,
            function () {
                jQuery(this).removeClass("gainingFocus");
                $slideShow.removeClass("inTransition");
                if (callback) {
                    callback();
                }
            }
        );
    }

    $slideShow
        .css({"position": "relative"})
        .mouseenter(function () {
            this.stop();
        })
        .mouseleave(function () {
            if(this.autoplay) this.start();
        });

    // Show the starting slide, hide the rest
    var $slides = $slideShow.find(this.slidesSelector);

    if (this.startingSlide == "random") {
        current = $slides.get(Math.floor(Math.random() * $slides.length));
    }
    else {
        current = $slides.get(0);
    }

    $slides.not(current)
        .css({"position": "absolute"})
        .hide();

    if (this.bulletControls) {
        $slideShow.get(0).selectBullet();
    }

    // Check the element's configuration to determine wether to start in
    // autoplay mode
    this.setAutoplay(this.autoplay);

    // Automatically hide navigation and bullet controls if there aren't
    // multiple slides
    this._toggleControls = function () {
        var method = ($slideShow.find(this.slidesSelector).length < 2) ? "hide" : "show";
        $slideShow.find(".navigation_button")[method]();
        $slideShow.find(".bullets")[method]();
    }

    this._toggleControls();
});

