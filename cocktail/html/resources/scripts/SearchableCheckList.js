/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2014
-----------------------------------------------------------------------------*/

cocktail.bind(".SearchableCheckList.search_enabled", function ($control) {

    var $checkList = $control.find(".check_list");
    var $entries = $checkList.find(".entry");
    var $groups = $checkList.find(".group");
    var entriesText = null;
    
    this.getSearchableText = function (item) {
        var $entry = jQuery(item);
        var text = $entry.text();
        var groupTitle = $entry.closest(".group").find(".group_label").text();
        if (groupTitle) {
            text = groupTitle + " " + text;
        }
        return text;
    }

    this.normalizeText = function (text) {
        return cocktail.normalizeLatin(text);
    }

    this.tokenizeText = function (text) {
        return text.split();
    }

    this.applySearch = function (query) {

        var control = $control.get(0);

        if (!query) {
            this.applyMatchState($entries, true);
        }
        else {
            if (entriesText == null) {
                entriesText = [];
                $entries.each(function () {
                    var text = control.getSearchableText(this);
                    text = control.normalizeText(text);
                    entriesText.push(text);
                });
            }

            var queryTokens = this.tokenizeText(this.normalizeText(query));

            $entries.each(function (i) {
                var text = entriesText[i];
                for (var i = 0; i < queryTokens.length; i++) {
                    if (text.indexOf(queryTokens[i]) == -1) {
                        control.applyMatchState(this, false);
                        return;
                    }
                }
                control.applyMatchState(this, true);
            });
        }

        $groups.each(function () {
            var $group = jQuery(this);
            control.applyMatchState($group, $group.find(".entry.match").length);
        });

        toggleSelectionLinks();
    }

    this.applyMatchState = function (element, match) {
        var $element = jQuery(element);
        if (match) {
            $element.addClass("match");
            $element.removeClass("no_match");
        }
        else {
            $element.removeClass("match");
            $element.addClass("no_match");
        }
    }

    var $searchControls = jQuery(cocktail.instantiate("cocktail.html.SearchableCheckList.searchControls"))
        .prependTo($control);

    function textBoxEventHandler() {
        $control.get(0).applySearch(this.value);
    }

    var $searchBox = $searchControls.find(".search_box")
        .on("search", textBoxEventHandler)
        .change(textBoxEventHandler)
        .keyup(textBoxEventHandler)
        .keydown(function (e) {

            // Disable the enter key
            if (e.keyCode == 13) {
                return false;
            }

            // Down key
            if (e.keyCode == 40) {
                $checkList.get(0).focusContent();
                return false;
            }
        });

    var $selectAllLink = $searchControls.find(".select_all_link");
    var $emptySelectionLink = $searchControls.find(".empty_selection_link");
    
    $selectAllLink.click(function () {
        $entries.filter(".match").each(function () {
            $checkList.get(0).setEntrySelected(this, true);
        });
        toggleSelectionLinks();
    });

    $emptySelectionLink.click(function () {
        $entries.filter(".match").each(function () {
            $checkList.get(0).setEntrySelected(this, false);
        });
        toggleSelectionLinks();
    });

    function toggleSelectionLinks() {

        var $allEntries = $entries.filter(".match");
        var $checkedEntries = $allEntries.filter(":has(input[type=checkbox]:checked)");

        if ($allEntries.length > $checkedEntries.length) {
            $selectAllLink.removeAttr("disabled");
        }
        else {
            $selectAllLink.attr("disabled", "disabled");
        }

        if ($checkedEntries.length) {
            $emptySelectionLink.removeAttr("disabled");
        }
        else {
            $emptySelectionLink.attr("disabled", "disabled");
        }
    }

    $checkList.get(0).topControl = $searchBox.get(0);

    $entries.find("input[type=checkbox]")
        .change(toggleSelectionLinks)
        .keydown(function (e) {
            if (e.keyCode == 191) {
                $searchBox.focus();
                return false;
            }
        });

    this.applySearch();
});

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

