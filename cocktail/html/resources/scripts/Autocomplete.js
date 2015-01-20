/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2015
-----------------------------------------------------------------------------*/

cocktail.bind(".Autocomplete", function ($autocomplete) {

    $autocomplete.attr("data-autocomplete-panel", "collapsed");

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

    this.entryMatchesAllTerms = function (entry, terms) {
        for (var t = 0; t < terms.length; t++) {
            if (!this.entryMatchesTerm(entry, terms[t])) {
                return false;
            }
        }
        return true;
    }

    this.entryMatchesTerm = function (entry, term) {
        if (!entry.normalizedText) {
            if (!entry.text) {
                entry.text = this.getSearchableText(entry);
            }
            entry.normalizedText = this.normalizeText(entry.text);
        }
        return this.textMatches(entry.normalizedText, term);
    }

    this.textMatches = function (text, term) {
        // term preceded by the start of the string or a non-letter character
        // (using XRegExp, since the native \b pattern is not Unicode aware)
        return XRegExp("(?:^|\\p{^L})" + term).test(text);
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
        }

        if (typeof(this.autocompleteSource) == "string") {
            var url = this.getAutocompleteURL(query);
            if (searchHttpRequest) {
                searchHttpRequest.abort();
            }
            searchHttpRequest = jQuery.getJSON(url)
                .done(searchComplete);
        }
        else if (this.autocompleteSource instanceof Array) {
            var matchingEntries = [];
            var terms = this.getQueryTerms(query);
            for (var i = 0; i < this.autocompleteSource.length; i++) {
                var entry = this.autocompleteSource[i];                
                if (this.entryMatchesAllTerms(entry, terms)) {
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
                currentInput = $input.val();
                panelTimeout = setTimeout(showPanel, $autocomplete[0].autocompleteDelay);
            }
        }
        else {
            currentInput = "";
            $autocomplete[0].setPanelVisible(false);
            $autocomplete[0].setSelectedEntry(null);
            return;
        }
    }

    function showPanel() {
        panelTimeout = null;
        searchHttpRequest = null;
        $autocomplete.attr("data-autocomplete-panel", "expanded");
        // TODO: show a "loading" sign, handle errors
        var autocomplete = $autocomplete[0];
        var query = $input.val();

        if (query != currentSearch) {
            var $panelEntries = $panel.find("[data-autocomplete-entry]");
            var highlightedValue = $highlightedEntry && $highlightedEntry.length && $highlightedEntry[0].autocompleteEntry.value;

            if (query != currentInput) {
                autocomplete.setSelectedEntry(null, true);
            }

            // Narrowing down the existing query: remove entries that no longer match
            if (autocomplete.narrowDown && currentSearch && query.indexOf(currentSearch) == 0) {
                currentSearch = query;
                var terms = autocomplete.getQueryTerms(query);
                $panelEntries.each(function () {
                    var $panelEntry = jQuery(this);
                    if (!autocomplete.entryMatchesAllTerms($panelEntry[0].autocompleteEntry, terms)) {
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
                        autocomplete.insertEntryDisplay($entryDisplay);
                    }

                    // Set the highlighted entry
                    // (preserve it if it still matches the search, otherwise clear it)
                    setHighlightedEntry(highlightedValue !== undefined ? getPanelEntry(highlightedValue) : null);
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

