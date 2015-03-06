/*-----------------------------------------------------------------------------


@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2013
-----------------------------------------------------------------------------*/

cocktail.bind(".MediaElementVideo", function ($video) {
    this.mediaElementOptions.success = function (mediaElement, domObject) {
        if ($video.attr("autoplay") && mediaElement.pluginType == 'flash') {
            mediaElement.addEventListener('canplay', function() {
                mediaElement.play();
            }, false);
        }
        $video.trigger("mediaElementReady");
    };
    $video.mediaelementplayer(this.mediaElementOptions);
});
