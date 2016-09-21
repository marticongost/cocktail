/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         September 2016
-----------------------------------------------------------------------------*/

cocktail.infiniteScroll = function (params) {

    var $element = jQuery(params.element);
    var $container = jQuery(params.container) || $element;
    var $scrollEventEmitter;
    var scrollable = params.scrollable || $container[0];
    var contentSelector = params.contentSelector;
    var nextPageSelector = params.nextPageSelector || ".Pager a.next";
    var nextPageURL = $element.find(nextPageSelector).attr("href");
    var direction = params.direction || "portrait";
    var autoTrigger = params.autoTrigger === undefined ? true : params.autoTrigger;
    var contentRequest;

    var overflowCheck = params.overflowCheck || function (viewportOffset, viewportSize, contentSize) {
        return viewportOffset >= contentSize - viewportSize * 2;
    };

    var insertContent = params.insertContent || function ($content) {
        $container.append($content);
        cocktail.init();
    };

    if (direction == "portrait") {
        var getViewportOffset = function () { return scrollable.scrollTop; };
        var getViewportSize = function () { return scrollable.offsetHeight; };
        var getContentSize = function () { return scrollable.scrollHeight; };
    }
    else if (direction == "landscape") {
        var getViewportOffset = function () { return scrollable.scrollLeft; };
        var getViewportSize = function () { return scrollable.offsetWidth; };
        var getContentSize = function () { return scrollable.scrollWidth; };
    }
    else {
        throw "Invalid direction for cocktail.infiniteScroll(); "
            + "expected 'portrait' or 'landscape', got " + direction + " instead.";
    }

    if (scrollable == document.body) {
        $scrollEventEmitter = jQuery(window);
        if (direction == "portrait") {
            getViewportSize = function () { return window.innerHeight; };
        }
        else if (direction == "landscape") {
            getViewportSize = function () { return window.innerWidth; };
        }
    }
    else {
        $scrollEventEmitter = jQuery(scrollable);
    }

    $element[0].loadContents = function (url) {

        if (contentRequest) {
            return;
        }

        $element
            .attr("data-infinite-scroll-state", "loading")
            .trigger({
                type: "infiniteScrollLoadingContent",
                $element: $element,
                $container: $container,
                url: url
            });

        contentRequest = jQuery.ajax({url: url})
            .done(function (text) {

                var doc = document.implementation.createHTMLDocument();
                doc.documentElement.innerHTML = text;

                nextPageURL = jQuery(nextPageSelector, doc).attr("href");

                var $content = jQuery(contentSelector, doc);

                $element.trigger({
                    type: "infiniteScrollInsertingContent",
                    $element: $element,
                    $container: $container,
                    document: doc,
                    $content: $content
                });

                insertContent($content);

                $element.trigger({
                    type: "infiniteScrollContentInserted",
                    $element: $element,
                    $container: $container,
                    document: doc,
                    $content: $content
                });

                $element.attr("data-infinite-scroll-state", "idle");
                contentRequest = null;
            });
    }

    $element[0].loadNextPage = function () {
        if (nextPageURL) {
            this.loadContents(nextPageURL);
        }
    }

    // Scroll event
    if (autoTrigger) {
        $scrollEventEmitter.on("scroll", function (e) {

            var viewportOffset = getViewportOffset();
            var viewportSize = getViewportSize();
            var contentSize = getContentSize();

            if (overflowCheck(viewportOffset, viewportSize, contentSize)) {
                $element[0].loadNextPage();
            }
        });
    }

    $element.attr("data-infinite-scroll-state", "idle");
}

