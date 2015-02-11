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
        var text = [];
        function descend(node) {
            if (node.nodeType == Document.TEXT_NODE) {
                text.push(node.nodeValue);
            }
            else if (node.nodeType == Document.ELEMENT_NODE) {
                for (var i = 0; i < node.childNodes.length; i++) {
                    descend(node.childNodes[i]);
                }
            }
        }
        descend(item);
        return text.join(" ");
    }

    searchable.normalizeText = function (text) {
        return cocktail.normalizeLatin(text);
    }

    searchable.tokenizeText = function (text) {
        return text.split(/\s+/);
    }

    searchable.matchTerms = function (text, terms, acceptPartialMatch /* = false */) {

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

        if (!acceptPartialMatch) {
            for (var t in matchedTerms) {
                if (!matchedTerms[t]) {
                    return null;
                }
            }
        }

        return matches;
    }

    searchable.applySearch = function (query) {

        var $entries = searchable.getSearchableEntries();
        var $matches = jQuery();

        if (!query) {
            searchable.applyMatchState($entries, true);
            $matches = $entries;
            if (highlighted) {
                $entries.each(function () {
                    searchable.clearHighlighting(this);
                });
            }
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
                if (searchable.matchTerms(text, queryTokens)) {
                    searchable.applyMatchState(this, true);
                    $matches.add(this);
                    if (highlighted) {
                        searchable.highlightSearchTerms(this, queryTokens);
                    }
                }
                else {
                    searchable.applyMatchState(this, false);
                    if (highlighted) {
                        searchable.clearHighlighting(this);
                    }
                }
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
    var highlighted = params && params.highlighted;

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

    searchable.clearHighlighting = function (entry) {

        // Remove previous marks
        var marks = entry.getElementsByTagName("mark");
        for (var i = marks.length - 1; i >= 0; i--) {
            var mark = marks[i];
            while (mark.firstChild) {
                mark.parentNode.insertBefore(mark.firstChild, mark);
            }
            mark.parentNode.removeChild(mark);
        }

        entry.normalize();
    }

    searchable.highlightSearchTerms = function (entry, terms) {

        this.clearHighlighting(entry);

        if (!terms.length) {
            return;
        }

        // Add new marks
        function highlightElement(element) {
            for (var i = 0; i < element.childNodes.length; i++) {
                var node = element.childNodes[i];
                if (node.nodeType == Document.TEXT_NODE) {
                    var text = node.nodeValue;
                    var normText = searchable.normalizeText(text);
                    var matches = searchable.matchTerms(normText, terms, true);
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
                    highlightElement(node);
                }
            }
        }

        highlightElement(entry);
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

    searchable.searchBox = $searchBox.get(0);
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

if (!String.prototype.trim) {
    String.prototype.trim = function () {
        var text = this.replace(/^\w+/, "");
        text = text.replace(/\w+$/, "");
        return text;
    }
}

