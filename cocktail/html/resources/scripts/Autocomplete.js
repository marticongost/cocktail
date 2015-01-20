/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2015
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
    this.autocompleteDelay = this.autocompleteDelay || 150;
    this.narrowDown = this.narrowDown === undefined ? true : false;
    this.highlighting = this.highlighting === undefined ? true : false;
    this.autoSelect = this.autoSelect === undefined ? true : false;

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
        var nonWordExpr = XRegExp("\\p{^L}");

        if (terms.length) {
            var expr = XRegExp(terms[0]);
        }
        else {
            var expr = XRegExp("(" + terms.join("|") + ")");
        }

        expr.forEach(text, function (match) {
            if (match.index == 0 || nonWordExpr.test(text.charAt(match.index - 1))) {
                matches.push(match);
            }
        });

        return matches.length ? matches : null;
    }

    this.normalizeText = cocktail.normalizeLatin;

    this.getQueryTerms = function (text) {
        var terms = text.split(/\s+/);
        var normalizedTerms = [];
        for (var i = 0; i < terms.length; i++) {
            normalizedTerms.push(this.normalizeText(terms[i]));
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

    this.setSelectedEntry = function (entry, preserveTextBox /* = false */) {
        this.selectedEntry = entry;

        if (!entry) {
            if (!preserveTextBox) {
                $input.val("");
            }
            $hidden.val("");
            $autocomplete.attr("data-autocomplete-selection", $input.val() ? "pending" : "empty");
        }
        else {
            if (!entry.text) {
                entry.text = this.getSearchableText(entry);
            }
            $input.val(entry.text);
            $hidden.val(entry.value); 
            $autocomplete.attr("data-autocomplete-selection", "complete");
        }

        currentInput = $input.val();
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
        else {
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

            if (query != currentInput) {
                autocomplete.setSelectedEntry(null, true);
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

                // Set the highlighted entry
                // (preserve it if it still matches the search, otherwise clear it)
                setHighlightedEntry(highlightedValue !== undefined ? getPanelEntry(highlightedValue) : null);
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

                    // Set the highlighted entry
                    // (preserve it if it still matches the search, otherwise clear it)
                    setHighlightedEntry(highlightedValue !== undefined ? getPanelEntry(highlightedValue) : null);
                });
            }

            // If there's only a single autocomplete entry, select it automatically
            if (autocomplete.autoSelect) {
                var $panelEntries = $panel.find("[data-autocomplete-entry]");
                if ($panelEntries.length == 1) {
                    autocomplete.setSelectedEntry($panelEntries[0].autocompleteEntry);
                    autocomplete.setPanelVisible(false);
                }
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
            $autocomplete[0].setPanelVisible(true);
            if (wasVisible) {
                var $nextEntry = $highlightedEntry.next();
                if ($nextEntry.length) {
                    setHighlightedEntry($nextEntry);
                }
            }
            return false;
        }
        else if (e.keyCode == KEY_UP) {
            $autocomplete[0].setPanelVisible(true);
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
        }
    });

    $input.change(processInput);

    $panel.mousedown(false);

    $panel.on("click", "[data-autocomplete-entry]", function () {
        $autocomplete[0].setSelectedEntry(this.autocompleteEntry);
        $autocomplete.attr("data-autocomplete-panel", "collapsed");
    });

    if (this.selectedEntry) {
        this.setSelectedEntry(this.selectedEntry);
        setHighlightedEntry(getPanelEntry(this.selectedEntry.value));
    }
});

jQuery(function () {
    jQuery(document).mousedown(function () {
        jQuery(".Autocomplete[data-autocomplete-panel='expanded']").each(function () {
            this.setPanelVisible(false);
        });
    });
});

