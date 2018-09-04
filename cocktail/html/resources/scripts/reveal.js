/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         March 2017
-----------------------------------------------------------------------------*/

cocktail.trackRevealedElements = function (options) {

    jQuery(options.element).each(function () {

        var element = this;
        var $element = jQuery(this);
        var revealedElements = {};
        var batchElements = [];
        var batchTimer;
        var scrollTimer;

        if (options.revealRatio === undefined) {
            options.revealRatio = 0.6;
        }

        if (options.scrollDelay === undefined) {
            options.scrollDelay = 50;
        }

        this.getRevealableElements = function () {
            return $element.find(options.entries).filter(":visible");
        }

        this.getRevealedElements = function () {
            return this.getRevealableElements().filter(function () {
                var id = cocktail.requireId(this);
                if (revealedElements[id]) {
                    return false;
                }
                return $element[0].elementIsRevealed(this);
            });
        }

        this.elementIsRevealed = function (item) {

            var x = 0;
            var y = 0;
            var w = item.offsetWidth;
            var h = item.offsetHeight;
            var totalSurface = w * h;

            while (item) {

                var isWindow = (item === document.body);
                var isScrollable = (
                    isWindow
                    || (
                        jQuery(item).css("overflow") != "visible"
                        && (
                            item.offsetWidth > item.scrollWidth
                            || item.offsetHeight > item.scrollHeight
                        )
                    )
                );

                if (isScrollable) {
                    var scrollLeft = isWindow ? window.scrollX : item.scrollLeft;
                    var scrollTop = isWindow ? window.scrollY : item.scrollTop;
                    var scrollWidth = isWindow ? window.innerWidth : item.scrollWidth;
                    var scrollHeight = isWindow ? window.innerHeight : item.scrollHeight;
                    var scrollRight = scrollLeft + scrollWidth;
                    var scrollBottom = scrollTop + scrollHeight;

                    if (x < scrollLeft) {
                        var visibleLeft = scrollLeft;
                    }
                    else if (x > scrollRight) {
                        var visibleLeft = scrollRight;
                    }
                    else {
                        var visibleLeft = x;
                    }

                    var x2 = x + w;
                    if (x2 < scrollLeft) {
                        var visibleRight = scrollLeft;
                    }
                    else if (x2 > scrollRight) {
                        var visibleRight = scrollRight;
                    }
                    else {
                        var visibleRight = x2;
                    }

                    if (y < scrollTop) {
                        var visibleTop = scrollTop;
                    }
                    else if (y > scrollBottom) {
                        var visibleTop = scrollBottom;
                    }
                    else {
                        var visibleTop = y;
                    }

                    var y2 = y + h;
                    if (y2 < scrollTop) {
                        var visibleBottom = scrollTop;
                    }
                    else if (y2 > scrollBottom) {
                        var visibleBottom = scrollBottom;
                    }
                    else {
                        var visibleBottom = y2;
                    }

                    var visibleSurface = (visibleRight - visibleLeft) * (visibleBottom - visibleTop);
                    var visibilityRatio = visibleSurface / totalSurface;

                    if (visibilityRatio < options.revealRatio) {
                        return false;
                    }
                }

                x += item.offsetLeft;
                y += item.offsetTop;
                item = item.offsetParent;
            }

            return true;
        }

        this.triggerRevealEvents = function () {
            var elements = this.getRevealedElements();
            if (elements.length) {
                elements.each(function () {
                    revealedElements[this.id] = true;
                });

                var delay = options.batchDelay;
                if (delay) {
                    batchElements.push.apply(batchElements, elements);
                    if (batchTimer) {
                        clearTimeout(batchTimer);
                    }
                    setTimeout(
                        function () {
                            $element.trigger({
                                type: "elementsRevealed",
                                elements: batchElements
                            });
                            batchElements = [];
                        },
                        delay
                    );
                }
                else {
                    $element.trigger({
                        type: "elementsRevealed",
                        elements: elements
                    });
                }
            }
        }

        var $containers = jQuery(window);
        var container = element;
        while (container) {
            $containers = $containers.add(container);
            container = container.parentNode;
        }

        $containers.on("scroll", function () {
            var delay = options.scrollDelay;
            if (delay) {
                if (scrollTimer) {
                    clearTimeout(scrollTimer);
                }
                scrollTimer = setTimeout(
                    function () {
                        $element[0].triggerRevealEvents();
                    },
                    delay
                );
            }
            else {
                element.triggerRevealEvents();
            }
        });

        $element.on("infiniteScrollContentInserted", function () {
            cocktail.waitForImages(element).done(function () {
                element.triggerRevealEvents();
            });
        });
    });
}

