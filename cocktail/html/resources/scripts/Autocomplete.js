/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         January 2015
-----------------------------------------------------------------------------*/

cocktail.bind(".Autocomplete", function ($autocomplete) {

    $autocomplete.attr("data-autocomplete-panel", "collapsed");
    $autocomplete.attr("data-autocomplete-status", "ready");

    var KEY_ENTER = 13;
    var KEY_UP = 38;
    var KEY_DOWN = 40;
    var KEY_ESCAPE = 27;

    var htmlExp = /<[^>]+>/g;
    var currentInput;
    var currentSearch;
    var $highlightedEntry;

    this.selectedEntry = this.selectedEntry || null;

    if (this.autocompleteDelay === undefined) {
        this.autocompleteDelay = 150;
    }

    if (this.narrowDown === undefined) {
        this.narrowDown = true;
    }

    if (this.highlighting === undefined) {
        this.highlighting = true;
    }

    if (this.autoSelect === undefined) {
        this.autoSelect = false;
    }

    if (this.allowFullList === undefined) {
        this.allowFullList = true;
    }

    if (this.autoExpand === undefined) {
        this.autoExpand = false;
    }

    if (this.selectTextOnFocus === undefined) {
        this.selectTextOnFocus = true;
    }

    var $input = $autocomplete.find(".text_box");

    var $hidden = jQuery("<input type='hidden'>")
        .attr("name", $input.attr("name"))
        .appendTo($autocomplete);

    $input
        .val("")
        .removeAttr("name");

    var $panelWrapper = jQuery("<div>")
        .addClass("panel_wrapper")
        .appendTo($autocomplete);

    var $panel = jQuery("<div>")
        .addClass("panel")
        .appendTo($panelWrapper);

    this.getSearchableText = function (entry) {
        return entry.label.replace(htmlExp, "");
    }

    this.entryMatches = function (entry, terms) {
        if (!entry.normalizedText) {
            if (!entry.text) {
                entry.text = this.getSearchableText(entry);
            }
            entry.normalizedText = this.normalizeText(entry.text);
        }
        return this.matchTerms(entry.normalizedText, terms);
    }

    this.matchTerms = function (text, terms) {

        // Find terms preceded by the start of the string or a non-letter
        // character. Using XRegExp, since the native \b pattern is not Unicode
        // aware. Also, Javascript doesn't support look-behind expressions. :(

        var matches = [];
        var matchedTerms = {};

        for (var i = 0; i < terms.length; i++) {
            matchedTerms[terms[i]] = false;
        }

        var nonWordExpr = XRegExp("\\p{^L}");

        if (terms.length) {
            var expr = XRegExp("(" + terms.join("|") + ")");
        }
        else {
            var expr = XRegExp(terms[0]);
        }

        expr.forEach(text, function (match) {
            if (match.index == 0 || nonWordExpr.test(text.charAt(match.index - 1))) {
                matches.push(match);
                matchedTerms[match[0]] = true;
            }
        });

        if (!matches.length) {
            return null;
        }

        for (var t in matchedTerms) {
            if (!matchedTerms[t]) {
                return null;
            }
        }

        return matches;
    }

    this.normalizeText = cocktail.normalizeLatin;

    this.getQueryTerms = function (text) {
        var terms = text.split(/\s+/);
        var normalizedTerms = [];
        for (var i = 0; i < terms.length; i++) {
            var term = this.normalizeText(terms[i]);
            if (term) {
                normalizedTerms.push(term);
            }
        }
        return normalizedTerms;
    }

    this.getAutocompleteURL = function (query) {
        return this.autocompleteSource.replace(/\bQUERY\b/, query);
    }

    this.search = function (query, callback) {

        function searchComplete(matchingEntries) {
            currentInput = query;
            currentSearch = query;
            searchHttpRequest = null;
            callback(matchingEntries);
            $autocomplete.attr("data-autocomplete-status", "ready");
        }

        if (typeof(this.autocompleteSource) == "string") {
            var url = this.getAutocompleteURL(query);
            if (searchHttpRequest) {
                searchHttpRequest.abort();
            }
            $autocomplete.attr("data-autocomplete-status", "searching");
            searchHttpRequest = jQuery.getJSON(url)
                .done(searchComplete);
        }
        else if (this.autocompleteSource instanceof Array) {
            var matchingEntries = [];
            var terms = this.getQueryTerms(query);
            for (var i = 0; i < this.autocompleteSource.length; i++) {
                var entry = this.autocompleteSource[i];
                if (this.entryMatches(entry, terms)) {
                    matchingEntries.push(entry);
                }
            }
            searchComplete(matchingEntries);
        }
    }

    this.setSelectedEntry = function (entry, preserveTextBox /* = false */, triggerEvents /* = true */) {

        var previousEntry = this.selectedEntry;
        var changed = (entry != this.selectedEntry);
        this.selectedEntry = entry;

        if (!entry) {
            if (!preserveTextBox) {
                $input.val("");
            }
            $hidden.val("");
            $autocomplete.attr("data-autocomplete-selection", $input.val() ? "pending" : "empty");
        }
        else {
            var textValue = entry.label || entry.text;
            if ($input.val() != textValue) {
                $input.val(textValue);
            }
            $hidden.val(entry.value);
            $autocomplete.attr("data-autocomplete-selection", "complete");
        }

        currentInput = $input.val();

        if (changed && (triggerEvents || triggerEvents === undefined)) {
            $autocomplete.trigger({type: "change", value: entry, previousValue: previousEntry});
        }
    }

    this.createEntryDisplay = function (entry) {
        return jQuery("<div>").html(entry.label || entry.text);
    }

    this.insertEntryDisplay = function ($display) {
        $display.appendTo($panel);
    }

    this.highlightSearchTerms = function ($display, terms) {

        var autocomplete = this;
        var display = $display[0];

        // Remove previous marks
        var marks = display.getElementsByTagName("mark");
        for (var i = marks.length - 1; i >= 0; i--) {
            var mark = marks[i];
            while (mark.firstChild) {
                mark.parentNode.insertBefore(mark.firstChild, mark);
            }
            mark.parentNode.removeChild(mark);
        }

        display.normalize();

        // Add new marks
        function highlight(element) {
            for (var i = 0; i < element.childNodes.length; i++) {
                var node = element.childNodes[i];
                if (node.nodeType == Document.TEXT_NODE) {
                    var text = node.nodeValue;
                    var normText = autocomplete.normalizeText(text);
                    var matches = autocomplete.matchTerms(normText, terms);
                    if (matches) {
                        var pos = 0;
                        for (var m = 0; m < matches.length; m++) {
                            var match = matches[m];

                            var textBefore = text.substring(pos, match.index);
                            if (textBefore) {
                                element.insertBefore(document.createTextNode(textBefore), node);
                                i++;
                            }

                            var matchingText = text.substr(match.index, match[0].length);
                            var mark = document.createElement("mark")
                            mark.appendChild(document.createTextNode(matchingText));
                            element.insertBefore(mark, node);

                            i++;
                            pos = match.index + match[0].length;
                        }
                        var trailingText = text.substr(pos);
                        if (trailingText) {
                            node.nodeValue = trailingText;
                        }
                        else {
                            element.removeChild(node);
                            i--;
                        }
                    }
                }
                else if (node.nodeType == Document.ELEMENT_NODE) {
                    highlight(node);
                }
            }
        }

        highlight(display);
    }

    var panelTimeout = null;
    var searchHttpRequest = null;

    this.setPanelVisible = function (visible) {
        cancelSearch();
        if (visible) {
            showPanel();
        }
        else if (!(this.autoExpand && $input.is(":focus") && $autocomplete.attr("data-autocomplete-selection") != "complete")) {
            $autocomplete.attr("data-autocomplete-panel", "collapsed");
        }
    }

    function cancelSearch() {
        if (panelTimeout) {
            clearTimeout(panelTimeout);
            panelTimeout = null;
        }
        if (searchHttpRequest) {
            searchHttpRequest.abort();
            searchHttpRequest = null;
            $autocomplete.attr("data-autocomplete-status", "ready");
        }
    }

    function processInput() {
        if ($input.val()) {
            if ($input.val() != currentInput) {
                cancelSearch();
                panelTimeout = setTimeout(showPanel, $autocomplete[0].autocompleteDelay);
            }
        }
        else {
            $autocomplete[0].setPanelVisible(false);
            $autocomplete[0].setSelectedEntry(null);
            return;
        }
    }

    function showPanel() {
        panelTimeout = null;
        searchHttpRequest = null;
        $autocomplete.attr("data-autocomplete-panel", "expanded");
        // TODO: handle errors
        var autocomplete = $autocomplete[0];
        var query = $input.val();

        if (query != currentSearch) {
            var $panelEntries = $panel.find("[data-autocomplete-entry]");
            var highlightedValue = $highlightedEntry && $highlightedEntry.length && $highlightedEntry[0].autocompleteEntry.value;
            var terms = autocomplete.getQueryTerms(query);

            if (!terms.length && !autocomplete.allowFullList) {
                autocomplete.setPanelVisible(false);
                return;
            }

            if (query != currentInput) {
                autocomplete.setSelectedEntry(null, true);
            }

            function afterFillingPanel() {

                // Set the highlighted entry
                // (preserve it if it still matches the search, otherwise clear it)
                setHighlightedEntry(highlightedValue !== undefined ? getPanelEntry(highlightedValue) : null);

                var $panelEntries = $panel.find("[data-autocomplete-entry]");

                // If there's only a single autocomplete entry, select it automatically
                if ($panelEntries.length == 1) {
                    if (autocomplete.autoSelect) {
                        autocomplete.setSelectedEntry($panelEntries[0].autocompleteEntry);
                        autocomplete.setPanelVisible(false);
                    }
                }
                // If there are no entries to display, hide the panel
                else if (!$panelEntries.length) {
                    autocomplete.setPanelVisible(false);
                }
            }

            // Narrowing down the existing query: remove entries that no longer match
            if (autocomplete.narrowDown && currentSearch && query.indexOf(currentSearch) == 0) {
                currentSearch = query;
                $panelEntries.each(function () {
                    var $panelEntry = jQuery(this);
                    if (autocomplete.entryMatches($panelEntry[0].autocompleteEntry, terms)) {
                        if (autocomplete.highlighting) {
                            autocomplete.highlightSearchTerms($panelEntry, terms);
                        }
                    }
                    else {
                        $panelEntry.remove();
                    }
                });
                afterFillingPanel();
            }
            // New query: clear the panel and start over
            else {
                $panelEntries.remove();
                autocomplete.search(query, function (entries) {

                    for (var i = 0; i < entries.length; i++) {
                        var entry = entries[i];
                        var $entryDisplay = autocomplete.createEntryDisplay(entry)
                            .attr("data-autocomplete-entry", entry.value);
                        $entryDisplay[0].autocompleteEntry = entry;
                        if (autocomplete.highlighting) {
                            autocomplete.highlightSearchTerms($entryDisplay, terms);
                        }
                        autocomplete.insertEntryDisplay($entryDisplay);
                    }
                    afterFillingPanel();
                });
            }
        }
    }

    function getPanelEntry(value) {
        return $panel.find("[data-autocomplete-entry='" + value + "']");
    }

    function setHighlightedEntry($newHighlightedEntry) {
        if (!$newHighlightedEntry || !$newHighlightedEntry.length) {
            $newHighlightedEntry = $panel.find("[data-autocomplete-entry]").first();
        }
        if ($highlightedEntry) {
            if ($newHighlightedEntry && $highlightedEntry[0] == $newHighlightedEntry[0]) {
                return;
            }
            $highlightedEntry.removeClass("highlighted");
        }
        $highlightedEntry = $newHighlightedEntry;
        if ($highlightedEntry && $highlightedEntry.length) {
            $highlightedEntry.addClass("highlighted");
            $highlightedEntry[0].scrollIntoView();
        }
    }

    $input.keyup(function (e) {
        if (e.keyCode == KEY_ESCAPE || e.keyCode == KEY_ENTER || e.keyCode == KEY_UP || e.keyCode == KEY_DOWN) {
            return false;
        }
        processInput();
    });

    $input.keydown(function (e) {
        if (e.keyCode == KEY_DOWN) {
            var wasVisible = ($autocomplete.attr("data-autocomplete-panel") == "expanded");
            if (this.value || $autocomplete[0].allowFullList) {
                $autocomplete[0].setPanelVisible(true);
            }
            if (wasVisible) {
                var $nextEntry = $highlightedEntry.next();
                if ($nextEntry.length) {
                    setHighlightedEntry($nextEntry);
                }
            }
            return false;
        }
        else if (e.keyCode == KEY_UP) {
            if (this.value || $autocomplete[0].allowFullList) {
                $autocomplete[0].setPanelVisible(true);
            }
            var $prevEntry = $highlightedEntry.prev();
            if ($prevEntry.length) {
                setHighlightedEntry($prevEntry);
            }
            return false;
        }
        else if (e.keyCode == KEY_ENTER) {
            if ($autocomplete.attr("data-autocomplete-panel") == "expanded") {
                if ($highlightedEntry.length) {
                    $autocomplete[0].setSelectedEntry($highlightedEntry[0].autocompleteEntry);
                    $autocomplete[0].setPanelVisible(false);
                }
                return false;
            }
        }
        else if (e.keyCode == KEY_ESCAPE) {
            if ($autocomplete.attr("data-autocomplete-panel") == "expanded") {
                $autocomplete[0].setPanelVisible(false);
                return false;
            }
            else {
                if ($autocomplete[0].selectedEntry) {
                    $autocomplete[0].setSelectedEntry(null);
                    return false;
                }
            }
        }
    });

    $input
        .change(function (e) {
            processInput(e);
            e.stopPropagation();
        })
        .focus(function () {
            if ($autocomplete[0].autoExpand && $autocomplete.attr("data-autocomplete-selection") != "complete") {
                $autocomplete[0].setPanelVisible(true);
            }
        })
        .click(function () {
            if ($autocomplete[0].selectTextOnFocus) {
                if (this.select) {
                    this.select();
                    return false;
                }
                else if (this.setSelectionRange) {
                    this.setSelectionRange(0, this.value.length);
                    return false;
                }
            }
        })
        .blur(function () {
            $autocomplete[0].setPanelVisible(false);
        });

    $panel.mousedown(false);

    $panel.on("click", "[data-autocomplete-entry]", function () {
        $autocomplete[0].setSelectedEntry(this.autocompleteEntry);
        $autocomplete.attr("data-autocomplete-panel", "collapsed");
    });

    if (this.selectedEntry) {
        this.setSelectedEntry(this.selectedEntry, false, false);
        setHighlightedEntry(getPanelEntry(this.selectedEntry.value));
    }
    else {
        $autocomplete.attr("data-autocomplete-selection", "empty");
    }
});

