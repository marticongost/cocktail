/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2013
-----------------------------------------------------------------------------*/

(function () {

    var sectioningContent = ["section", "article", "aside", "nav"];
    var sectioningContentSelector = sectioningContent.join(", ");

    var selector = "";
    var glue = "";

    for (var i = 0; i < sectioningContent.length; i++) {
        selector += glue + ".outline_root " + sectioningContent[i];
        glue = ", ";
    }

    function getLevel($element) {
        var level = 0;
        while ($element.length && !$element.is(".outline_root")) {
            if ($element.is(sectioningContentSelector)) {
                level++;
            }
            $element = $element.parent();
        }
        return level;
    }

    cocktail.bind(selector, function ($element) {
        $element.addClass("s");
        $element.addClass("s" + getLevel($element));
    });

    cocktail.bind(
        ".outline_root h1,"
      + ".outline_root h2,"
      + ".outline_root h3,"
      + ".outline_root h4,"
      + ".outline_root h5,"
      + ".outline_root h6",
        function ($heading) {
            $heading.addClass("h");
            var sLevel = getLevel($heading.parent());
            var hLevel = Number($heading[0].tagName.charAt(1));
            $heading.addClass("h" + (sLevel + hLevel));
        }
    );
})();

