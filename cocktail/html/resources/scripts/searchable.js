/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2014
-----------------------------------------------------------------------------*/

cocktail.searchable = function (searchable, params /* = null */) {

    var $searchable = jQuery(searchable);
    searchable = $searchable.get(0);

    searchable.getSearchableEntries = function () {
        return $searchable.find(params && params.entriesSelector || ".entry");
    }

    searchable.getSearchableText = function (item) {
        return jQuery(item).text();
    }

    searchable.normalizeText = function (text) {
        return cocktail.normalizeLatin(text);
    }

    searchable.tokenizeText = function (text) {
        return text.split(/\s+/);
    }

    searchable.applySearch = function (query) {

        var $entries = searchable.getSearchableEntries();
        var $matches = jQuery();

        if (!query) {
            searchable.applyMatchState($entries, true);
            $matches = $entries;
        }
        else {
            // Normalize and tokenize the search query
            var queryTokens = searchable.tokenizeText(searchable.normalizeText(query));

            // Flag matching / non matching entries
            $entries.each(function (i) {
                
                // Obtain and normalize the searchable text for each entry
                var text = this.searchableText;
                if (text === undefined) {
                    text = this.searchableText = searchable.normalizeText(
                        searchable.getSearchableText(this)
                    );
                }

                // All tokens must be found for the entry to match
                for (var i = 0; i < queryTokens.length; i++) {
                    if (text.indexOf(queryTokens[i]) == -1) {
                        searchable.applyMatchState(this, false);
                        return;
                    }
                }

                searchable.applyMatchState(this, true);
                $matches = $matches.add(this);
            });
        }

        // Flag matching / non matching entry groups
        if (params && params.entryGroupsSelector) {
            var $groups = $searchable.find(params.entryGroupsSelector);
            $groups.each(function () {
                searchable.applyMatchState(this, jQuery(this).find($matches).length);
            });
        }

        $searchable.trigger("searched", {
            query: query,
            matches: $matches
        });
    }

    var matchClass = params && params.matchCSSClass || "match";
    var noMatchClass = params && params.noMatchCSSClass || "no_match";

    searchable.applyMatchState = function (target, match) {
        var $target = jQuery(target);
        if (match) {
            $target.addClass(matchClass);
            $target.removeClass(noMatchClass);
        }
        else {
            $target.removeClass(matchClass);
            $target.addClass(noMatchClass);
        }
    }

    function searchBoxEventHandler() {
        searchable.applySearch(this.value);
    }

    var $searchBox = $searchable.find(params && params.searchBoxSelector || "input[type=search]")
        .on("search", searchBoxEventHandler)
        .change(searchBoxEventHandler)
        .keyup(searchBoxEventHandler)
        .keydown(function (e) {
            // Disable the enter key
            if (e.keyCode == 13) {
                return false;
            }
        });
}

cocktail.latinNormalization = {
    a: /[àáâãäåāăą]/g,
    A: /[ÀÁÂÃÄÅĀĂĄ]/g,
    e: /[èééêëēĕėęě]/g,
    E: /[ÈÉĒĔĖĘĚ]/g,
    i: /[ìíîïìĩīĭ]/g,
    I: /[ÌÍÎÏÌĨĪĬ]/g,
    o: /[òóôõöōŏő]/g,
    O: /[OÒÓÔÕÖŌŎŐ]/g,
    u: /[ùúûüũūŭů]/g,
    U: /[ÙUÚÛÜŨŪŬŮ]/g
};

cocktail.normalizeLatin = function (text) {
    text = text.trim();
    if (!text.length) {
        return text;
    }
    for (var c in cocktail.latinNormalization) {
        text = text.replace(cocktail.latinNormalization[c], c);
    }
    return text.toLowerCase();
}

