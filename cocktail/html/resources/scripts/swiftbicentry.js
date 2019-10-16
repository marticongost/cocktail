/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2014
-----------------------------------------------------------------------------*/

cocktail.bind(".SWIFTBICEntry", function ($entry) {

    var $expl = $entry.find(".swiftbic_explanation");
    var $summary = $expl.find("summary");

    var $link = jQuery("<a>")
        .addClass("swiftbic_explanation_link")
        .html($summary.html())
        .attr("href", "javascript:")
        .click(function () {
            cocktail.showDialog($dialog);
            cocktail.center($dialog.get(0));
        });

    var $linkWrapper = jQuery("<div>")
        .addClass("swiftbic_explanation_link_wrapper")
        .append($link)
        .insertBefore($expl);

    $summary.remove();
    var $dialog = jQuery(cocktail.instantiate("cocktail.html.SWIFTBICEntry.swiftbic_explanation_dialog"));
    $dialog.find(".swiftbic_explanation_dialog_body").html($expl.html());
    $dialog.find(".swiftbic_explanation_dialog_close_button").click(cocktail.closeDialog);
    $expl.remove();
});

