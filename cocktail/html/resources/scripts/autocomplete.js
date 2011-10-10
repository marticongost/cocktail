/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2009
-----------------------------------------------------------------------------*/

jQuery(function () {
    jQuery(document).mousedown(function () {
        jQuery(".autocomplete_dropdown").removeClass("unfolded");
    });
});

cocktail.autocomplete = function (input, params /* optional */) {

    var KEY_ENTER = 13;
    var KEY_UP = 38;
    var KEY_DOWN = 40;

    var resultsContainer = document.createElement("div");
    resultsContainer.className = "autocomplete_results_container";

    var dropdown = document.createElement("div");
    dropdown.className = "autocomplete_dropdown";
    resultsContainer.appendChild(dropdown);
    
    var $input = jQuery(input);
    var $dropdown = jQuery(dropdown);
    $input.after(resultsContainer);
    $input.addClass("autocomplete");
 
    $dropdown.mousedown(function () { return false; });

    var delay = params && params.delay || 100;
    var uri = params && params.uri;
    var options = params && params.options;
    var timeout = null;
    var normalize = params && params.normalize;
    var cached = !params || !("cached" in params) || params.cached;
    var cache = cached ? {} : null;

    var htmlExp = /<[^>]+>/g;
    var focused = false;
    var lastQuery = null;

    if (normalize === undefined) {
        var normalizationMap = {
            "àáâä": "a",
            "èéêë": "i",
            "ìíîï": "i",
            "òóôö": "o",
            "ùúûü": "u"
        }
        var normalizationCharMap = {}; 
        var regexpStr = "";
        for (var chars in normalizationMap) {
            regexpStr += chars;
            for (var i = 0; i < chars.length; i++) {
                normalizationCharMap[chars.charAt(i)] = normalizationMap[chars];
            }
        }
        var regexp = new RegExp("[" + regexpStr + "]", "g");
        normalize = function (s) {
            s = s.toLowerCase();
            s = s.replace(
                regexp,
                function (c) { return normalizationCharMap[c]; }
            );
            s = s.replace(htmlExp, "");
            return s;
        }
    }

    if (options) {
        var normalizedOptions = [];
        for (var i = 0; i < options.length; i++) {
            var option = options[i];
            if (typeof(option) == "string") {
                option = {label: option};
            }
            if (normalize) {
                option.normalizedLabel = normalize(option.label);
            }
            else {
                option.normalizedLabel = option.label;
            }
            normalizedOptions.push(option);
        }
        options = normalizedOptions;
    }

    $input.keydown(function (e) {

        if (e.keyCode == KEY_UP) {
            selectPreviousEntry();
            return false;
        }
        else if (e.keyCode == KEY_DOWN) {
            selectNextEntry();
            return false;
        }
        else if (e.keyCode == KEY_ENTER) {
            if ($dropdown.is(".unfolded") && $selectedEntry) {
                chooseOption($selectedEntry.get(0).autocompleteOption);
                setResultsDisplayed(false);
                return false;
            }
        }

        if (timeout) {
            clearTimeout(timeout);
        }
        if (this.value.length) {
            timeout = setTimeout(update, delay);
        }
        else {
            update();
        }
    });

    $input.click(update);
    $input.focus(function () { focused = true; });
    $input.blur(function () {
        focused = false;
        setResultsDisplayed(false);
    });

    $input.bind("optionSelected", function (e, option) {
        chooseOption(option);        
    });

    function chooseOption(option) {
        input.value = option.label.replace(htmlExp, "");
        lastQuery = input.value;
        setResultsDisplayed(false);
    }

    var $selectedEntry = null;

    function selectEntry(entry) {
        $dropdown.find(".autocomplete_entry.selected").removeClass("selected");
        if (entry) {
            $selectedEntry = jQuery(entry);
            $selectedEntry.addClass("selected");
        }
        else {
            $selectedEntry = null;
        }
    }

    function selectNextEntry() {
        if ($selectedEntry) {
            var $nextEntry = $selectedEntry.next(".autocomplete_entry");
            if ($nextEntry.length) {
                selectEntry($nextEntry);
            }
        }
    }

    function selectPreviousEntry() {
        if ($selectedEntry) {
            var $previousEntry = $selectedEntry.prev(".autocomplete_entry");
            if ($previousEntry.length) {
                selectEntry($previousEntry);
            }
        }
    }

    function selectFirstEntry() {
        selectEntry($dropdown.find(".autocomplete_entry").first());
    }

    function update() {        
        var query = input.value;
        if (query.length) {
            if (query != lastQuery) {
                lastQuery = query;
                input._autocomplete(query);
            }
        }
        else {
            setResultsDisplayed(false);
        }
    }

    input._autocomplete = function (query) {
        this._findAutocompleteResults(query, function (query, results, alreadyCached) {

            $dropdown.empty();
            
            if (!results.length || !focused) {
                setResultsDisplayed(false);
            }
            else {
                for (var i = 0; i < results.length; i++) {
                    input._renderAutocompleteOption(results[i]);
                }
                setResultsDisplayed(true);
            }

            selectFirstEntry();

            if (cache && !alreadyCached) {
                cache[query] = results;
            }
        });
    }

    input._renderAutocompleteOption = function (option) {
        var optionEntry = document.createElement("div");
        optionEntry.className = "autocomplete_entry";
        optionEntry.innerHTML = option.label;
        optionEntry.autocompleteOption = option;
        jQuery(optionEntry).click(function () {
            $input.trigger("optionSelected", this.autocompleteOption);
        });
        dropdown.appendChild(optionEntry);
    }

    input._findAutocompleteResults = function (query, resultsReady) {

        if (normalize) {
            query = normalize(query);
        }
        
        var results = cache && cache[query];

        if (results) {
            resultsReady(query, results, true);
        }
        else {
            if (options) {
                var results = [];
                for (var i = 0; i < options.length; i++) {
                    var option = options[i];
                    if (this.autocompleteMatch(option, query)) {
                        results.push(option);
                    }
                }
                resultsReady(query, results);
            }
            else {
                if (typeof(uri) == "string") {
                    var requestURI = uri;
                }
                else {
                    var requestURI = uri(query);
                }
                jQuery.getJSON(requestURI, function (data) {
                    var items = [];
                    for (var i = 0; i < data.length; i++) {
                        var item = data[i];
                        if (typeof(item) == "string") {
                            item = {label: item};
                        }
                        items.push(item);
                    }
                    resultsReady(query, items);
                });
            }
        }
    }

    input.autocompleteMatch = function (option, query) {
        return option.normalizedLabel.indexOf(query) != -1;
    }
   
    function setResultsDisplayed(displayed) {
        if (displayed) {
            jQuery(".autocomplete_dropdown").removeClass("unfolded");
            $dropdown.addClass("unfolded");
        }
        else {            
            $dropdown.removeClass("unfolded");
        }
    }
}
