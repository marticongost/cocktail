/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2014
-----------------------------------------------------------------------------*/

cocktail.bind(".SearchableCheckList.search_enabled", function ($control) {

    var $searchControls = jQuery(cocktail.instantiate("cocktail.html.SearchableCheckList.searchControls"))
        .prependTo($control);

    cocktail.searchable(this, this.searchableOptions);

    this.getSearchableText = function (item) {
        var $entry = jQuery(item);
        var text = $entry.text();
        var groupTitle = $entry.closest(".group").find(".group_label").text();
        if (groupTitle) {
            text = groupTitle + " " + text;
        }
        return text;
    }

    var $checkList = $control.find(".check_list");

    var $searchBox = $searchControls.find(".search_box")
        .keydown(function (e) {
            // Down key
            if (e.keyCode == 40) {
                $checkList.get(0).focusContent();
                return false;
            }
        });

    var $selectAllLink = $searchControls.find(".select_all_link");
    var $emptySelectionLink = $searchControls.find(".empty_selection_link");

    $selectAllLink.click(function () {
        $checkList.get(0).selectEntries(":selectable-entry");
    });

    $emptySelectionLink.click(function () {
        $checkList.get(0).clearSelection(":selectable-entry");
    });

    function toggleSelectionLinks() {

        var $allEntries = $checkList.get(0).getEntries(":selectable-entry.match");
        var $checkedEntries = $allEntries.filter(".selected");

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

    $checkList.get(0).getEntries().find("input[type=checkbox]")
        .keydown(function (e) {
            if (e.keyCode == 191) {
                $searchBox.focus();
                return false;
            }
        });

    $checkList.on("selectionChanged", toggleSelectionLinks);
    $control
        .on("searched", toggleSelectionLinks)
        .addClass("exposable")
        .on("exposed", toggleSelectionLinks);

    this.applySearch($searchBox.val());
});

