/*-----------------------------------------------------------------------------

TODO: Select all / none links
TODO: Styles!
TODO: Grouping
TODO: Drag & drop

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2014
-----------------------------------------------------------------------------*/

cocktail.bind(".SplitSelector.search_enabled", function ($control) {

    function chooseSelection() {
        var $entries = $eligibleItemsContainer[0].getSelection().filter(":visible");
        $selectedItemsContainer[0].clearSelection(null, true);
        $eligibleItemsContainer[0].clearSelection(null, true);
        $entries.each(function () { chooseEntry(this); });
        $selectedItemsContainer[0].selectEntries($entries);
        $selectedItemsContainer[0].focusContent();
    }

    function dropSelection() {
        var $entries = $selectedItemsContainer[0].getSelection().filter(":visible");
        $selectedItemsContainer[0].clearSelection(null, true);
        $eligibleItemsContainer[0].clearSelection(null, true);
        $entries.each(function () { dropEntry(this); });
        $eligibleItemsContainer[0].selectEntries($entries);
        $eligibleItemsContainer[0].focusContent();
    }

    function chooseEntry(entry, sort /* = true */) {
        if ($selectedItemsContainer.find(entry).length) {
            return false;
        }
        $eligibleItemsContainer[0].setEntrySelected(entry, false);
        insertEntry($selectedItemsContainer, entry, sort);
        entry.appendChild(entry.splitSelectorHiddenInput);
        $control.trigger({type: "change"});
        return true;
    }

    function dropEntry(entry, sort /* = true */) {
        if ($eligibleItemsContainer.find(entry).length) {
            return false;
        }
        $selectedItemsContainer[0].setEntrySelected(entry, false);
        insertEntry($eligibleItemsContainer, entry, sort);
        if (entry.splitSelectorHiddenInput.parentNode) {
            entry.removeChild(entry.splitSelectorHiddenInput);
        }
        $(entry).find("input[type=checkbox]").removeAttr("checked");
        $control.trigger({type: "change"});
        return true;
    }

    function insertEntry($container, entry, sort /* = true */) {
        var inserted = false;

        if (sort || sort === undefined) {
            $container.children().each(function () {
                if (this.splitSelectorIndex > entry.splitSelectorIndex) {
                    jQuery(entry).insertBefore(this);
                    inserted = true;
                    return false;
                }
            });
        }

        if (!inserted) {
            $container.append(entry);
        }
    }

    function toggleButtons() {
        if ($selectedItemsContainer[0].getSelection().filter(":visible").length) {
            $dropButton.removeAttr("disabled");
        }
        else {
            $dropButton.attr("disabled", "disabled");
        }

        if ($eligibleItemsContainer[0].getSelection().filter(":visible").length) {
            $chooseButton.removeAttr("disabled");
        }
        else {
            $chooseButton.attr("disabled", "disabled");
        }
    }

    var $splitPanels = jQuery(cocktail.instantiate("cocktail.html.SplitSelector.splitPanels"))
        .prependTo($control);

    var $selectedItemsPanel = $splitPanels.find(".selected_items_panel");
    var $selectedItemsContainer = $selectedItemsPanel.find(".split_panel_content");
    var $eligibleItemsPanel = $splitPanels.find(".eligible_items_panel");
    var $eligibleItemsContainer = $eligibleItemsPanel.find(".split_panel_content");

    // Toggle buttons for both panels
    var $dropButton = $selectedItemsPanel.find(".toggle_button").click(dropSelection);
    var $chooseButton = $eligibleItemsPanel.find(".toggle_button").click(chooseSelection);

    // Double click / enter key toggles selected entries from one panel to another
    $selectedItemsContainer.on("activated", dropSelection);
    $eligibleItemsContainer.on("activated", chooseSelection);

    // Focus the selected items container when pressing the right key from the eligible
    // panels container
    $selectedItemsContainer.on("keydown", ".entry", function (e) {
        if (e.keyCode == 39) {
            if ($eligibleItemsContainer[0].getEntries(":selectable-entry").length) {
                $eligibleItemsContainer[0].focusContent();
            }
            return false;
        }
    });

    // Focus the selected items container when pressing the left key from the eligible
    // panels container
    $eligibleItemsContainer.on("keydown", ".entry", function (e) {
        if (e.keyCode == 37) {
            if ($selectedItemsContainer[0].getEntries(":selectable-entry").length) {
                $selectedItemsContainer[0].focusContent();
            }
            return false;
        }
    });

    // Move the entries to their starting panel
    $control.find(".check_list").find(".entry").each(function (index) {

        $(this).removeClass("selected");
        var $check = $(this).find("input[type=checkbox]");

        this.splitSelectorIndex = index;
        this.splitSelectorHiddenInput = document.createElement("input");
        this.splitSelectorHiddenInput.type = "hidden";
        this.splitSelectorHiddenInput.name = $check.attr("name");
        this.splitSelectorHiddenInput.value = $check.attr("value");

        if ($check.is(":checked")) {
            chooseEntry(this, false);
        }
        else {
            dropEntry(this, false);
        }

        $check
            .removeAttr("name")
            .removeAttr("value")
            .removeAttr("checked");
    });

    var $searchControls = jQuery(cocktail.instantiate("cocktail.html.SplitSelector.searchControls"))
        .prependTo($control);

    cocktail.searchable(this, {
        entryGroupsSelector: ".group"
    });

    var $checkList = $control.find(".check_list");

    // Pressing the down key from the search box focuses the panesl
    var $searchBox = $searchControls.find(".search_box")
        .keydown(function (e) {
            if (e.keyCode == 40) {
                // Try to focus the selected items container first
                if ($selectedItemsContainer[0].getEntries(":selectable-entry").length) {
                    $selectedItemsContainer.get(0).focusContent();
                }
                // If there are no entries there, try to focus the eligible items container
                else if ($eligibleItemsContainer[0].getEntries(":selectable-entry").length) {
                    $eligibleItemsContainer.get(0).focusContent();
                }
                return false;
            }
        });

    // Hitting the up key from the first entry of a split panel focuses the search box
    $selectedItemsContainer[0].topControl = $searchBox.get(0);
    $eligibleItemsContainer[0].topControl = $searchBox.get(0);

    // Pressing the / key focuses the search box
    $splitPanels.on("keydown", "input[type=checkbox]", function (e) {
        if (e.keyCode == 191) {
            $searchBox.focus();
            return false;
        }
    });

    $selectedItemsContainer.on("selectionChanged", toggleButtons);
    $eligibleItemsContainer.on("selectionChanged", toggleButtons);
    $control
        .on("searched", toggleButtons)
        .addClass("exposable")
        .on("exposed", toggleButtons);

    this.getValue = function () {
        var value = [];
        $selectedItemsContainer[0].getEntries().each(function () {
            value.push(this.splitSelectorHiddenInput.value);
        });
        return value;
    }

    this.setValue = function (value) {

        // Remove entries that are no longer selected
        $selectedItemsContainer[0].getEntries().each(function () {
            var entryValue = this.splitSelectorHiddenInput.value;
            if (!value || value.indexOf(entryValue) == -1) {
                dropEntry(this);
            }
        })

        // Add entries that were not selected
        if (value) {
            $eligibleItemsContainer[0].getEntries().each(function () {
                if (value.indexOf(this.splitSelectorHiddenInput.value) != -1) {
                    chooseEntry(this);
                }
            });
        }
    }

    this.getPossibleValues = function () {
        var values = this.getValue();
        $eligibleItemsContainer[0].getEntries().each(function () {
            values.push(this.splitSelectorHiddenInput.value);
        });
        return values;
    }

    this.applySearch($searchBox.val());
});

