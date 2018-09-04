/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2012
-----------------------------------------------------------------------------*/

function onYouTubeIframeAPIReady() {
    cocktail.youTubeAPIReady = true;
    jQuery(document).trigger("youTubeAPIReady");
}

cocktail.bind(".YouTubePlayer.scriptable_video_player", function ($player) {

    var api = null;

    function createPlayer() {
        new YT.Player($player[0], {
            events: {
                onReady: function (e) {
                    api = e.target;
                    $player.trigger("playerReady");
                },
                onStateChange: function (e) {
                    var state = e.data;
                    if (state == YT.PlayerState.PLAYING) {
                        $player.addClass("prevent_autoplay");
                    }
                    else if (state == YT.PlayerState.ENDED) {
                        $player.removeClass("prevent_autoplay");
                    }
                }
            }
        });
    }

    if (cocktail.youTubeAPIReady) {
        createPlayer();
    }
    else {
        jQuery(document).one("youTubeAPIReady", createPlayer);
    }

    this.youTubeAPI = function (callback) {
        if (api) {
            callback(api);
        }
        else {
            $player.one("playerReady", function () { callback(api); });
        }
    }

    this.play = function () {
        this.youTubeAPI(function (api) { api.playVideo(); });
    }

    this.pause = function () {
        this.youTubeAPI(function (api) { api.stopVideo(); });
    }

    this.stop = function () {
        this.youTubeAPI(function (api) {
            api.seekTo(0);
            api.stopVideo();
        });
    }

    this.seekTo = function (seconds) {
        this.youTubeAPI(function (api) { api.seekTo(seconds); });
    }
});

