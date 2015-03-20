/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2014
-----------------------------------------------------------------------------*/

(function () {

    function TreeNode(label) {
        this.label = label;
        this.value = null;
        this.children = [];
    }

    TreeNode.fromElement = function (element, levels, depth) {

        var $element = jQuery(element);
        var node = new TreeNode();
        depth = depth || 0;
        var levelInfo = levels && depth < levels.length && levels[depth];

        if ($element.is(".radio_entry")) {
            node.label = $element.find("label").html();
            node.value = $element.find("input").attr("value");
        }
        else {
            if ($element.is(".group")) {
                node.label = $element.children(".group_label").html();
            }
            $element.children(".group, .radio_entry").each(function () {
                node.children.push(TreeNode.fromElement(this, levels, depth + 1));
            });
            if (levelInfo && levelInfo.sorted) {
                node.children.sort(function (a, b) {
                    if (a.normLabel > b.normLabel) {
                        return 1;
                    }
                    else if (a.normLabel < b.normLabel) {
                        return -1;
                    }
                    return 0;
                });
            }
            node.children.unshift(new TreeNode(levelInfo && levelInfo.null_label));
        }

        if (node.label) {
            node.normLabel = cocktail.normalizeLatin(node.label);
        }

        return node
    }

    TreeNode.prototype.createSelector = function () {
        var select = document.createElement("select");
        select.treeNode = this;
        for (var i = 0; i < this.children.length; i++) {
            var option = document.createElement("option");
            option.treeNode = this.children[i];
            option.value = this.children[i].value;
            option.innerHTML = this.children[i].label;
            select.appendChild(option);
        }
        return select;
    }

    cocktail.bind(".DrillDownSelector", function ($drillDown) {

        $drillDown.find("input[value='']").closest(".radio_entry").remove();
        var levels = this.levels;
        var tree = TreeNode.fromElement($drillDown, levels);
        var initialValue = $drillDown.find("input:checked").attr("value");

        var $hidden = jQuery("<input type='hidden'>")
            .attr("name", $drillDown.find("input").attr("name"))
            .attr("value", initialValue)
            .appendTo(this);

        $drillDown.find(".group, .radio_entry").remove();

        var $selectors = jQuery("<div>")
            .addClass("selectors")
            .appendTo(this);

        function addSelector(node) {
            var $level = jQuery("<div>")
                .addClass("level");

            var depth = $selectors.find(".level").length;
            if (levels && depth < levels.length && levels[depth].label) {
                jQuery("<div>")
                    .addClass("level_label")
                    .html(levels[depth].label)
                    .appendTo($level);
            }

            $level.append(node.createSelector());
            $level.appendTo($selectors);
            return $level;
        }

        function getSelectedOption() {
            return $selectors.find("select").last().find("option:selected");
        }

        $selectors.on("change", "select", function () {
            jQuery(this).closest(".level").nextAll().remove();
            var $option = getSelectedOption();
            if ($option.length && $option[0].treeNode.children.length) {
                addSelector($option[0].treeNode);
            }
            $hidden.attr("value", $option[0].treeNode.value || "");
        });

        var initialPath = [];

        function findInitialPath(node) {
            if (node.value == initialValue) {
                initialPath.push(node);
                return true;
            }
            var inPath = false;
            for (var i = 0; i < node.children.length; i++) {
                inPath = inPath || findInitialPath(node.children[i]);
            }
            if (inPath) {
                initialPath.push(node);
            }
            return inPath;
        }

        findInitialPath(tree);

        for (var i = initialPath.length - 1; i >= 0; i--) {
            if (initialPath[i].children.length) {
                var $level = addSelector(initialPath[i]);
                if (i - 1 >= 0) {
                    $level
                    .find("option")
                    .filter(function () {
                        return this.treeNode === initialPath[i - 1];
                    })
                        .prop("selected", true);
                }
            }
        }
    });
})();

