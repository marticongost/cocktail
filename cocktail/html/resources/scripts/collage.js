/*-----------------------------------------------------------------------------


@author:        Marti Congost
@contact:       marti.congost@whads.com
@organization:  Whads / Accent SL
@since:         May 2015
-----------------------------------------------------------------------------*/

cocktail.collage = {};

cocktail.collage.defaultOptions = {
    containerWidth: "auto",
    layout: {
        type: "cocktail.collage.RowLayout"
    },
    contentSelector: null,
    containerSelector: null,
    updateOnResize: true,
    updateOnResizeDelay: 200
};

cocktail.collage.init = function (element, options /* = {} */) {

    var $element = jQuery(element);
    element = $element[0];
    element.collage = {};

    var contentReady = false;

    for (var key in cocktail.collage.defaultOptions) {
        var customValue = options && options[key];
        element.collage[key] = (customValue === undefined) ? cocktail.collage.defaultOptions[key] : customValue;
    }

    if (element.collage.containerSelector) {
        var $container = $element.find(element.collage.containerSelector).first();
    }
    else {
        var $container = $element;
    }

    if (!(element.collage.layout instanceof cocktail.collage.Layout) && element.collage.layout.type) {
        var layoutOptions = element.collage.layout;
        var collageType = cocktail.getVariable(layoutOptions.type);
        delete element.collage.layout.type;
        element.collage.layout = new collageType(layoutOptions);
    }

    $element.attr("data-cocktail-collage-layout", element.collage.layout.layoutId);

    element.collage.rearrange = function () {

        if (!contentReady) {
            return;
        }

        var items = [];
        this.getContent()
            .css("display", "inline-block")
            .each(function () {
                var item = element.collage.getContentInfo(this);
                item.content = this;
                items.push(item);
            });

        this.layout.apply(element, items);
        $element.addClass("layout_ready");
    }

    element.collage.getContainer = function () {
        return $container;
    }

    element.collage.getContainerWidth = function () {
        var width = this.containerWidth;
        if (width == "auto") {
            width = $container.width();
        }
        return width;
    }

    element.collage.getContent = function () {
        if (this.contentSelector) {
            return $container.find(this.contentSelector).filter(":visible");
        }
        else {
            return $container.children(":visible");
        }
    }

    element.collage.getContentInfo = function (content) {
        var $content = jQuery(content);

        var width = $content.data("cocktail-collage-width");
        if (!width) {
            var width = $content.outerWidth();
            $content.data("cocktail-collage-width", width);
        }

        var height = $content.data("cocktail-collage-height");
        if (!height) {
            var height = $content.outerHeight();
            $content.data("cocktail-collage-height", height);
        }

        return {
            width: width,
            height: height
        };
    }

    if (element.collage.updateOnResize) {

        var resizeDelayTimer = null;

        function updateOnResize() {
            // If the collage has been removed from the document,
            // disable the resize event handler
            if (!element.parentNode) {
                jQuery(window).off("resize", null, updateOnResize);
                return;
            }
            if (element.collage.updateOnResize) {
                if (resizeDelayTimer) {
                    clearTimeout(resizeDelayTimer);
                }
                resizeDelayTimer = setTimeout(
                    function () {
                        element.collage.rearrange();
                    },
                    element.collage.updateOnResizeDelay
                );
            }
        }
        jQuery(window).on("resize", updateOnResize);
    }

    // Rearrange the collage as soon as its images have been loaded
    cocktail.waitForImages($container).done(function () {
        contentReady = true;
        element.collage.rearrange();
    });
}

cocktail.collage.Layout = function (options /* = {} */) {
    this.absolutePosition = options && options.absolutePosition || false;
}

cocktail.collage.Layout.prototype.layoutId = "";
cocktail.collage.Layout.prototype.absolutePosition = false;

cocktail.collage.Layout.prototype.apply = function (element, contentInfo) {

    var dist = this.getDistribution(contentInfo, element.collage.getContainerWidth());

    this.updateCollage(element, dist);

    for (var i = 0; i < dist.tiles.length; i++) {
        var tile = dist.tiles[i];
        this.updateTile(tile);
    }
}

cocktail.collage.Layout.prototype.getDistribution = function (items, containerWidth) {
    return [];
}

cocktail.collage.Layout.prototype.updateCollage = function (element, dist) {
    if (this.absolutePosition) {
        element.collage.getContainer()
            .css("position", "relative")
            .height(dist.height);
    }
}

cocktail.collage.Layout.prototype.updateTile = function (tile) {
    this.setTileSize(tile);
    if (this.absolutePosition) {
        tile.content.style.position = "absolute";
        this.setTilePosition(tile);
    }
}

cocktail.collage.Layout.prototype.setTileSize = function (tile) {
    if (tile.content.setSize) {
        tile.content.setSize(tile.width, tile.height);
    }
    else {
        jQuery(tile.content)
            .outerWidth(tile.width)
            .outerHeight(tile.height);
    }
}

cocktail.collage.Layout.prototype.setTilePosition = function (tile) {
    jQuery(tile.content)
        .css("left", tile.left + "px")
        .css("top", tile.top + "px");
}

cocktail.collage.RowLayout = function (options /* = null */) {
    cocktail.collage.Layout.call(this, options);
    this.maxRowHeight = options && options.maxRowHeight || 200;
    this.expandLastRow = options ? options.expandLastRow : false;
    this.expandLastRowThreshold = options ? options.expandLastRowThreshold : null;
    this.hspacing = options && options.hspacing || 0;
    this.vspacing = options && options.vspacing || 0;
}

cocktail.collage.RowLayout.prototype = new cocktail.collage.Layout();
cocktail.collage.RowLayout.prototype.layoutId = "rows";

cocktail.collage.RowLayout.prototype.getDistribution = function (items, containerWidth) {

    if (!items.length) {
        return [];
    }

    // Work around rounding errors
    containerWidth--;

    var layout = this;
    var tiles = [];
    var row = null;
    var rowWidth = 0;
    var rowTop = 0;

    function resizeRow() {

        var adjRatio = containerWidth / rowWidth;
        var adjWidth = 0;

        for (var i = 0; i < row.length; i++) {
            if (i > 0) {
                adjWidth += layout.hspacing;
            }
            var tile = row[i];
            tile.left = adjWidth;
            tile.width = Math.floor(tile.width * adjRatio);
            tile.height = Math.floor(tile.height * adjRatio);
            adjWidth += tile.width;
        }

        var diff = containerWidth - adjWidth;
        if (diff > 0) {
            tile.width += diff;
        }

        rowTop += tile.height + layout.vspacing;
        row = null;
    }

    for (var i = 0; i < items.length; i++) {

        if (row === null) {
            row = [];
            rowWidth = 0;
        }

        var item = items[i];
        var tile = {
            item: item,
            content: item.content,
            left: rowWidth + (row.length ? this.hspacing : 0),
            top: rowTop,
            width: Math.floor(item.width * this.maxRowHeight / item.height),
            height: this.maxRowHeight
        };
        if (row.length) {
            rowWidth += this.hspacing;
        }
        row.push(tile);
        tiles.push(tile);
        rowWidth += tile.width;

        if (rowWidth >= containerWidth) {
            resizeRow();
        }
    }

    if (
        row
        && this.expandLastRow
        && (
            this.expandLastRowThreshold === null
            || rowWidth * this.expandLastRowThreshold >= containerWidth
        )
    ) {
        resizeRow();
    }

    return {
        tiles: tiles,
        height: rowTop + (row ? tile.height : 0)
    };
}

