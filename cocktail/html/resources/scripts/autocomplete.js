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

    var delay = params && params.delay || 50;
    var uri = params && params.uri;
    var options = params && params.options;
    var timeout = null;
    var normalize = params && params.normalize;
    var cached = !params || !("cached" in params) || params.cached;
    var cache = cached ? {} : null;

    var htmlExp = /<[^>]+>/g;
    var focused = false;
    
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

    $input.keydown(function () {
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
    $input.blur(function () { focused = false; });

    $input.bind("optionSelected", function (e, option) {
        selectOption(option);        
    });

    function selectOption(option) {
        input.value = option.label.replace(htmlExp, "");
        setResultsDisplayed(false);
    }

    function update() {
        $dropdown.empty();
        var query = input.value;
        if (query.length) {
            input.autocomplete(query);
        }
        else {
            setResultsDisplayed(false);
        }
    }

    input.autocomplete = function (query) {
        this.findAutocompleteResults(query, function (query, results, cached) {
            if (!results.length || !focused) {
                setResultsDisplayed(false);
            }
            else {
                for (var i = 0; i < results.length; i++) {
                    input.renderAutocompleteOption(results[i]);
                }
                setResultsDisplayed(true);
            }

            if (cache && !cached) {
                cache[query] = results;
            }
        });
    }

    input.renderAutocompleteOption = function (option) {
        var optionEntry = document.createElement("div");
        optionEntry.innerHTML = option.label;
        optionEntry.autocompleteOption = option;
        jQuery(optionEntry).click(function () {
            $input.trigger("optionSelected", this.autocompleteOption);
        });
        dropdown.appendChild(optionEntry);
    }

    input.findAutocompleteResults = function (query, resultsReady) {

        if (normalize) {
            query = normalize(query);
        }
        
        var results = cache && cache[results];

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
                throw new Exception("AJAX not implemented yet");
                // TODO: ajax
            }
        }
    }

    input.autocompleteMatch = function (option, query) {
        return option.normalizedLabel.indexOf(query) != -1;
    }
   
    function setResultsDisplayed(displayed) {
        if (displayed) {
            $dropdown.addClass("unfolded");
        }
        else {
            $dropdown.removeClass("unfolded");
        }
    }
}
