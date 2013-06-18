/*-----------------------------------------------------------------------------


@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			June 2013
-----------------------------------------------------------------------------*/

cocktail.bind(".IssuuViewer", function ($viewer) {

    window.onIssuuReadersLoaded = function() {
        var viewer = window.IssuuReaders.get($viewer.get(0).configId);
        viewer.setPageNumber($viewer.get(0).pageNumber);
    };

});

