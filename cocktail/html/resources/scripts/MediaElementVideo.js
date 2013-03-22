/*-----------------------------------------------------------------------------


@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2013
-----------------------------------------------------------------------------*/

cocktail.bind(".MediaElementVideo", function ($video) {
    var video = this;
    this.mediaElementOptions.success = function (mediaElement, domObject) { 
        video.mediaElement = mediaElement;
        if ($video.attr("autoplay") && mediaElement.pluginType == 'flash') {
            mediaElement.addEventListener('canplay', function() {
                mediaElement.play();
                $(video.layers).css({"display": "none"});
            }, false);
        }
        $video.trigger("mediaElementReady");
    };
    $video.mediaelementplayer(this.mediaElementOptions);
});
