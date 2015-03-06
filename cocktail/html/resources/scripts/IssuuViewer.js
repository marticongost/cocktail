/*-----------------------------------------------------------------------------


@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			June 2013
-----------------------------------------------------------------------------*/

function onIssuuReadersLoaded() {
    cocktail.issuuAPIReady = true;
    jQuery(document).trigger("issuuAPIReady");
}

cocktail.bind(".IssuuViewer", function ($viewer) {

    var api = null;

    function prepareAPI() {
        api = IssuuReaders.get($viewer.get(0).configId);
        $viewer.trigger("issuuViewerReady", api);
    }

    if (cocktail.issuuAPIReady) {
        prepareAPI();
    }
    else {
        jQuery(document).one("issuuAPIReady", prepareAPI);
    }

    this.issuuAPI = function (callback) {
        if (api) {
            callback(api);
        }
        else {
            $viewer.one("issuuViewerReady", function (e, api) { callback.call(this, api); });
        }
    }

    if (this.pageNumber) {
        this.issuuAPI(function (api) {
            api.setPageNumber(this.pageNumber);
        });
    }
});

